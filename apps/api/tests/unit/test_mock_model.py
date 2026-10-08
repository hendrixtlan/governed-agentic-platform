import pytest

from agentic_platform.llm.provider import MockAgentModel


@pytest.mark.asyncio
async def test_mock_planner_selects_payment_and_incident_capabilities():
    plan = await MockAgentModel().plan(
        "Why are payments failing and is there an incident?", "customer-123"
    )
    assert "payments" in plan.capabilities
    assert "servicenow" in plan.capabilities
    assert "jira" in plan.capabilities
