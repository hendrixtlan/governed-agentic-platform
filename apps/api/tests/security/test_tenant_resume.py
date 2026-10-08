import pytest

from agentic_platform.persistence.workflow_registry import WorkflowRegistry


@pytest.mark.asyncio
async def test_workflow_registry_preserves_tenant_owner():
    registry = WorkflowRegistry()
    await registry.bind("wf-a", "TENANT_A")
    assert await registry.owner("wf-a") == "TENANT_A"
    assert await registry.owner("missing") is None
