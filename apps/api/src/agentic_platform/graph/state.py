import operator
from typing import Annotated, Literal, TypedDict

Capability = Literal[
    "salesforce",
    "servicenow",
    "jira",
    "glean",
    "oracle_hcm",
    "payments",
]


class EvidenceItem(TypedDict):
    source: str
    reference: str
    summary: str


class WorkflowState(TypedDict, total=False):
    request: str
    subject: str
    capabilities: list[Capability]
    capability_index: int
    evidence: Annotated[list[EvidenceItem], operator.add]
    errors: Annotated[list[str], operator.add]
    analysis: str
    proposed_action: dict | None
    approval_status: str
    created_action_ref: str | None
    final_answer: str
