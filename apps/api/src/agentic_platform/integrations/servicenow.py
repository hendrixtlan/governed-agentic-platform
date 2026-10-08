from __future__ import annotations

import httpx

from agentic_platform.config import get_settings
from agentic_platform.observability.audit import audit


class ServiceNowMutationAdapter:
    """Narrow mutation client for the TypeScript enterprise-tool boundary."""

    def __init__(self):
        self.base_url = get_settings().enterprise_tools_url

    async def create_incident(
        self,
        *,
        tenant_id: str,
        title: str,
        description: str,
        priority: str,
        idempotency_key: str,
    ) -> str:
        headers = {
            "X-Trusted-Tenant-Id": tenant_id,
            "Idempotency-Key": idempotency_key,
        }
        payload = {
            "title": title,
            "description": description,
            "priority": priority,
        }
        async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
            response = await client.post(
                "/servicenow/incidents",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            incident_id = response.json()["incident_id"]
        audit(
            "servicenow_create_incident",
            tenant_id=tenant_id,
            incident_id=incident_id,
            idempotency_key=idempotency_key,
        )
        return incident_id

    async def verify_incident(self, *, tenant_id: str, incident_id: str) -> bool:
        headers = {"X-Trusted-Tenant-Id": tenant_id}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
            response = await client.get(
                f"/servicenow/incidents/{incident_id}",
                headers=headers,
            )
            if response.status_code == 404:
                return False
            response.raise_for_status()
            return bool(response.json().get("exists"))


servicenow_mutations = ServiceNowMutationAdapter()
