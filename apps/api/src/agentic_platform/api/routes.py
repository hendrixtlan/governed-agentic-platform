from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from langgraph.types import Command

from agentic_platform.api.schemas import (
    InvestigationResponse,
    ResumeInvestigationRequest,
    StartInvestigationRequest,
)
from agentic_platform.auth.context import ExecutionContext, Principal
from agentic_platform.auth.dependencies import authenticate_demo
from agentic_platform.graph.builder import graph
from agentic_platform.observability.audit import audit
from agentic_platform.persistence.workflow_registry import workflow_registry

router = APIRouter()


def make_context(principal: Principal, workflow_id: str) -> ExecutionContext:
    return ExecutionContext(
        user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        roles=principal.roles,
        workflow_id=workflow_id,
        trace_id=str(uuid4()),
    )


def normalize_result(workflow_id: str, result: dict) -> InvestigationResponse:
    interrupts = result.get("__interrupt__", ())
    if interrupts:
        first = interrupts[0]
        value = first.value if hasattr(first, "value") else first
        return InvestigationResponse(
            workflow_id=workflow_id,
            status="awaiting_approval",
            answer=result.get("analysis"),
            approval_request=value,
            errors=result.get("errors", []),
        )
    return InvestigationResponse(
        workflow_id=workflow_id,
        status="completed",
        answer=result.get("final_answer") or result.get("analysis"),
        errors=result.get("errors", []),
    )


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/v1/investigations", response_model=InvestigationResponse)
async def start_investigation(
    body: StartInvestigationRequest,
    principal: Principal = Depends(authenticate_demo),
) -> InvestigationResponse:
    workflow_id = str(uuid4())
    await workflow_registry.bind(workflow_id, principal.tenant_id)
    ctx = make_context(principal, workflow_id)
    config = {"configurable": {"thread_id": workflow_id}}
    audit(
        "workflow_start",
        workflow_id=workflow_id,
        tenant_id=ctx.tenant_id,
        user_id=ctx.user_id,
        trace_id=ctx.trace_id,
    )
    try:
        result = await graph.ainvoke(
            {
                "request": body.question,
                "subject": body.subject,
                "evidence": [],
                "errors": [],
            },
            config=config,
            context=ctx,
        )
    except Exception as exc:
        audit("workflow_failure", workflow_id=workflow_id, error_type=type(exc).__name__)
        raise HTTPException(status_code=500, detail="Workflow execution failed") from exc
    return normalize_result(workflow_id, result)


@router.post(
    "/v1/investigations/{workflow_id}/resume",
    response_model=InvestigationResponse,
)
async def resume_investigation(
    workflow_id: str,
    body: ResumeInvestigationRequest,
    principal: Principal = Depends(authenticate_demo),
) -> InvestigationResponse:
    owner = await workflow_registry.owner(workflow_id)
    if owner is None or owner != principal.tenant_id:
        # 404 avoids exposing workflow existence across tenants.
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not ({"ops_manager", "admin"} & set(principal.roles)):
        raise HTTPException(status_code=403, detail="Approval role required")

    ctx = make_context(principal, workflow_id)
    config = {"configurable": {"thread_id": workflow_id}}
    try:
        result = await graph.ainvoke(
            Command(resume={"approved": body.approved, "comment": body.comment}),
            config=config,
            context=ctx,
        )
    except Exception as exc:
        audit(
            "workflow_resume_failure",
            workflow_id=workflow_id,
            error_type=type(exc).__name__,
        )
        raise HTTPException(status_code=500, detail="Workflow resume failed") from exc
    return normalize_result(workflow_id, result)
