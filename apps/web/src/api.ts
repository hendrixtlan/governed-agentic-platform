export type InvestigationResponse = {
  workflow_id: string;
  status: "completed" | "awaiting_approval";
  answer?: string;
  approval_request?: {
    type: string;
    workflow_id: string;
    message: string;
    proposed_action: Record<string, unknown>;
  };
  errors: string[];
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const identityHeaders = {
  "X-User-Id": "jose",
  "X-Tenant-Id": "ACME",
  "X-Roles": "analyst,ops_manager"
};

export async function startInvestigation(
  question: string,
  subject: string
): Promise<InvestigationResponse> {
  const response = await fetch(`${API_URL}/v1/investigations`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...identityHeaders },
    body: JSON.stringify({ question, subject })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function resumeInvestigation(
  workflowId: string,
  approved: boolean,
  comment?: string
): Promise<InvestigationResponse> {
  const response = await fetch(`${API_URL}/v1/investigations/${workflowId}/resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...identityHeaders },
    body: JSON.stringify({ approved, comment })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}
