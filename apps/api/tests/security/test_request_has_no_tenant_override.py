from agentic_platform.api.schemas import StartInvestigationRequest


def test_request_contract_does_not_expose_tenant_id():
    fields = StartInvestigationRequest.model_fields
    assert "tenant_id" not in fields
