from typing import Any, Literal

from pydantic import BaseModel, Field


class StartInvestigationRequest(BaseModel):
    question: str = Field(min_length=3, max_length=8000)
    subject: str = Field(min_length=1, max_length=256)


class ResumeInvestigationRequest(BaseModel):
    approved: bool
    comment: str | None = Field(default=None, max_length=2000)


class InvestigationResponse(BaseModel):
    workflow_id: str
    status: Literal["completed", "awaiting_approval"]
    answer: str | None = None
    approval_request: dict[str, Any] | None = None
    errors: list[str] = Field(default_factory=list)
