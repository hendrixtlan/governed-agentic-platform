from __future__ import annotations

import httpx

from agentic_platform.config import get_settings
from agentic_platform.graph.state import EvidenceItem


class EnterpriseToolsClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or get_settings().enterprise_tools_url

    async def _get(self, path: str, tenant_id: str, params: dict[str, str]) -> dict:
        headers = {"X-Trusted-Tenant-Id": tenant_id}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
            response = await client.get(path, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

    async def salesforce(self, tenant_id: str, subject: str) -> list[EvidenceItem]:
        data = await self._get("/salesforce/account", tenant_id, {"subject": subject})
        return data["evidence"]

    async def servicenow(self, tenant_id: str, subject: str) -> list[EvidenceItem]:
        data = await self._get("/servicenow/incidents", tenant_id, {"subject": subject})
        return data["evidence"]

    async def jira(self, tenant_id: str, subject: str) -> list[EvidenceItem]:
        data = await self._get("/jira/issues", tenant_id, {"subject": subject})
        return data["evidence"]

    async def glean(self, tenant_id: str, query: str) -> list[EvidenceItem]:
        data = await self._get("/glean/search", tenant_id, {"query": query})
        return data["evidence"]

    async def oracle_hcm(self, tenant_id: str, subject: str) -> list[EvidenceItem]:
        data = await self._get("/oracle-hcm/owner", tenant_id, {"subject": subject})
        return data["evidence"]
