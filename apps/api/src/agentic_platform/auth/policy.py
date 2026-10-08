from agentic_platform.auth.context import ExecutionContext
from agentic_platform.observability.audit import audit


class PolicyEngine:
    READ_ACTIONS = {
        "salesforce.read",
        "servicenow.read",
        "jira.read",
        "glean.search",
        "oracle_hcm.read_owner",
        "payments.read",
    }

    async def require(
        self,
        ctx: ExecutionContext,
        action: str,
        resource: str = "*",
    ) -> None:
        # Replace with Amazon Verified Permissions/Cedar or enterprise PDP.
        if action in self.READ_ACTIONS:
            allowed = bool(ctx.roles)
        elif action == "servicenow.create_incident":
            allowed = bool({"ops_manager", "admin"} & set(ctx.roles))
        else:
            allowed = False

        audit(
            "authorization_decision",
            workflow_id=ctx.workflow_id,
            trace_id=ctx.trace_id,
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id,
            action=action,
            resource=resource,
            allowed=allowed,
        )

        if not allowed:
            raise PermissionError(f"Not authorized for {action}")


policy = PolicyEngine()
