from __future__ import annotations

from typing import Literal

from langgraph.graph import END
from langgraph.runtime import Runtime
from langgraph.types import Command, interrupt

from agentic_platform.auth.context import ExecutionContext
from agentic_platform.auth.policy import policy
from agentic_platform.graph.contracts import ApprovalDecision
from agentic_platform.graph.state import WorkflowState
from agentic_platform.integrations.client import EnterpriseToolsClient
from agentic_platform.integrations.servicenow import servicenow_mutations
from agentic_platform.llm.provider import AgentModel
from agentic_platform.observability.audit import audit
from agentic_platform.repositories.payments import payments

TOOLS = EnterpriseToolsClient()


def create_nodes(model: AgentModel):
    async def plan_node(
        state: WorkflowState,
        runtime: Runtime[ExecutionContext],
    ) -> Command[Literal["route_capability"]]:
        plan = await model.plan(state["request"], state.get("subject", "unknown"))
        capabilities = list(dict.fromkeys(plan.capabilities))
        audit(
            "plan_created",
            workflow_id=runtime.context.workflow_id,
            capabilities=capabilities,
        )
        return Command(
            update={"capabilities": capabilities, "capability_index": 0},
            goto="route_capability",
        )

    def route_capability_node(
        state: WorkflowState,
    ) -> Command[
        Literal[
            "salesforce",
            "servicenow",
            "jira",
            "glean",
            "oracle_hcm",
            "payments",
            "synthesize",
        ]
    ]:
        capabilities = state.get("capabilities", [])
        index = state.get("capability_index", 0)
        if index >= len(capabilities):
            return Command(goto="synthesize")
        capability = capabilities[index]
        return Command(update={"capability_index": index + 1}, goto=capability)

    async def _read_tool(
        state: WorkflowState,
        runtime: Runtime[ExecutionContext],
        action: str,
        call,
    ) -> Command[Literal["route_capability"]]:
        ctx = runtime.context
        try:
            await policy.require(ctx, action, state.get("subject", "*"))
            items = await call(ctx)
            return Command(update={"evidence": items}, goto="route_capability")
        except Exception as exc:
            audit(
                "tool_failure",
                workflow_id=ctx.workflow_id,
                action=action,
                error_type=type(exc).__name__,
            )
            return Command(
                update={"errors": [f"{action}: {type(exc).__name__}"]},
                goto="route_capability",
            )

    async def salesforce_node(state, runtime):
        return await _read_tool(
            state,
            runtime,
            "salesforce.read",
            lambda ctx: TOOLS.salesforce(ctx.tenant_id, state.get("subject", "unknown")),
        )

    async def servicenow_node(state, runtime):
        return await _read_tool(
            state,
            runtime,
            "servicenow.read",
            lambda ctx: TOOLS.servicenow(ctx.tenant_id, state.get("subject", "unknown")),
        )

    async def jira_node(state, runtime):
        return await _read_tool(
            state,
            runtime,
            "jira.read",
            lambda ctx: TOOLS.jira(ctx.tenant_id, state.get("subject", "unknown")),
        )

    async def glean_node(state, runtime):
        return await _read_tool(
            state,
            runtime,
            "glean.search",
            lambda ctx: TOOLS.glean(ctx.tenant_id, state["request"]),
        )

    async def oracle_hcm_node(state, runtime):
        return await _read_tool(
            state,
            runtime,
            "oracle_hcm.read_owner",
            lambda ctx: TOOLS.oracle_hcm(ctx.tenant_id, state.get("subject", "unknown")),
        )

    async def payments_node(state, runtime):
        return await _read_tool(
            state,
            runtime,
            "payments.read",
            lambda ctx: payments.get_recent_failures(
                tenant_id=ctx.tenant_id, subject=state.get("subject", "unknown")
            ),
        )

    async def synthesize_node(
        state: WorkflowState,
        runtime: Runtime[ExecutionContext],
    ) -> Command[Literal["approval", "__end__"]]:
        result = await model.analyze(
            state["request"],
            state.get("evidence", []),
            state.get("errors", []),
        )
        proposed_action = (
            result.proposed_action.model_dump() if result.proposed_action is not None else None
        )
        update = {
            "analysis": result.summary,
            "proposed_action": proposed_action,
            "final_answer": result.summary,
        }
        audit(
            "analysis_complete",
            workflow_id=runtime.context.workflow_id,
            proposed_action=bool(proposed_action),
            references=result.supporting_references,
        )
        if proposed_action:
            return Command(update=update, goto="approval")
        return Command(update=update, goto=END)

    def approval_node(
        state: WorkflowState,
        runtime: Runtime[ExecutionContext],
    ) -> Command[Literal["execute_action", "__end__"]]:
        proposal = state.get("proposed_action")
        if not proposal:
            return Command(goto=END)

        decision = interrupt(
            {
                "type": "approval_required",
                "workflow_id": runtime.context.workflow_id,
                "proposed_action": proposal,
                "message": "Approve or reject this enterprise mutation.",
            },
            response_schema=ApprovalDecision,
        )
        parsed = (
            decision
            if isinstance(decision, ApprovalDecision)
            else ApprovalDecision.model_validate(decision)
        )
        audit(
            "human_approval",
            workflow_id=runtime.context.workflow_id,
            user_id=runtime.context.user_id,
            approved=parsed.approved,
        )
        if not parsed.approved:
            return Command(
                update={
                    "approval_status": "rejected",
                    "final_answer": (
                        state.get("analysis", "")
                        + "\n\nProposed action was not executed because it was rejected."
                    ),
                },
                goto=END,
            )
        return Command(update={"approval_status": "approved"}, goto="execute_action")

    async def execute_action_node(
        state: WorkflowState,
        runtime: Runtime[ExecutionContext],
    ) -> Command[Literal["verify_action", "__end__"]]:
        ctx = runtime.context
        proposal = state.get("proposed_action")
        if not proposal:
            return Command(goto=END)
        try:
            await policy.require(ctx, "servicenow.create_incident", state.get("subject", "*"))
        except PermissionError:
            return Command(
                update={
                    "approval_status": "authorization_denied",
                    "final_answer": (
                        state.get("analysis", "")
                        + "\n\nThe action was approved but not executed because the caller "
                        "is not authorized for this mutation."
                    ),
                },
                goto=END,
            )

        idempotency_key = f"{ctx.workflow_id}:servicenow:create_incident"
        incident_id = await servicenow_mutations.create_incident(
            tenant_id=ctx.tenant_id,
            title=proposal["title"],
            description=proposal["description"],
            priority=proposal["priority"],
            idempotency_key=idempotency_key,
        )
        return Command(update={"created_action_ref": incident_id}, goto="verify_action")

    async def verify_action_node(
        state: WorkflowState,
        runtime: Runtime[ExecutionContext],
    ) -> Command[Literal["__end__"]]:
        incident_id = state.get("created_action_ref")
        if not incident_id:
            return Command(goto=END)
        verified = await servicenow_mutations.verify_incident(
            tenant_id=runtime.context.tenant_id,
            incident_id=incident_id,
        )
        suffix = (
            f"\n\nApproved action executed and verified: {incident_id}."
            if verified
            else f"\n\nAction returned {incident_id}, but verification failed."
        )
        return Command(update={"final_answer": state.get("analysis", "") + suffix}, goto=END)

    return {
        "plan": plan_node,
        "route_capability": route_capability_node,
        "salesforce": salesforce_node,
        "servicenow": servicenow_node,
        "jira": jira_node,
        "glean": glean_node,
        "oracle_hcm": oracle_hcm_node,
        "payments": payments_node,
        "synthesize": synthesize_node,
        "approval": approval_node,
        "execute_action": execute_action_node,
        "verify_action": verify_action_node,
    }
