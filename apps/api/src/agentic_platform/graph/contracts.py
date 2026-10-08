from typing import Literal

from pydantic import BaseModel, Field

from agentic_platform.graph.state import Capability


class InvestigationPlan(BaseModel):
    capabilities: list[Capability] = Field(
        description="Allowed governed capabilities required for the investigation"
    )
    rationale: str


class ActionProposal(BaseModel):
    system: Literal["servicenow"]
    action: Literal["create_incident"]
    title: str
    description: str
    priority: Literal["P1", "P2", "P3", "P4"]


class AnalysisResult(BaseModel):
    summary: str
    supporting_references: list[str]
    proposed_action: ActionProposal | None = None


class ApprovalDecision(BaseModel):
    approved: bool
    comment: str | None = None
