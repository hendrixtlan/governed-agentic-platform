from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class ExecutionContext:
    user_id: str
    tenant_id: str
    roles: tuple[str, ...]
    workflow_id: str
    trace_id: str


class Principal(BaseModel):
    user_id: str
    tenant_id: str
    roles: tuple[str, ...]
