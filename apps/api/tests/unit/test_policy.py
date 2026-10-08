import pytest

from agentic_platform.auth.context import ExecutionContext
from agentic_platform.auth.policy import PolicyEngine


def ctx(roles):
    return ExecutionContext(
        user_id="u1",
        tenant_id="ACME",
        roles=roles,
        workflow_id="wf1",
        trace_id="t1",
    )


@pytest.mark.asyncio
async def test_read_allowed_for_authenticated_role():
    await PolicyEngine().require(ctx(("analyst",)), "jira.read")


@pytest.mark.asyncio
async def test_write_denied_for_analyst():
    with pytest.raises(PermissionError):
        await PolicyEngine().require(ctx(("analyst",)), "servicenow.create_incident")


@pytest.mark.asyncio
async def test_write_allowed_for_ops_manager():
    await PolicyEngine().require(ctx(("ops_manager",)), "servicenow.create_incident")
