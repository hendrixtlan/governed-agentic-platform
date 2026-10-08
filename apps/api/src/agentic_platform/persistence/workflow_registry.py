from __future__ import annotations

import asyncio


class WorkflowRegistry:
    """Local-only tenant ownership registry.

    Production should persist this binding transactionally with workflow/thread
    creation. Never allow callers to resume arbitrary thread IDs.
    """

    def __init__(self):
        self._tenants: dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def bind(self, workflow_id: str, tenant_id: str) -> None:
        async with self._lock:
            self._tenants[workflow_id] = tenant_id

    async def owner(self, workflow_id: str) -> str | None:
        async with self._lock:
            return self._tenants.get(workflow_id)


workflow_registry = WorkflowRegistry()
