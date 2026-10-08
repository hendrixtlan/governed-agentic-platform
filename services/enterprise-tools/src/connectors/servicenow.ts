import { Evidence } from "../types.js";

const createdIncidents = new Map<string, string>();

export async function getIncidents(tenantId: string, subject: string): Promise<Evidence[]> {
  return [{
    source: "servicenow",
    reference: "INC-9821",
    summary: `Active payment-gateway degradation affecting ${subject}; tenant=${tenantId}; status=Investigating.`
  }];
}

export async function createIncident(
  tenantId: string,
  request: { title: string; description: string; priority: string },
  idempotencyKey: string
): Promise<string> {
  const scopedKey = `${tenantId}:${idempotencyKey}`;
  const existing = createdIncidents.get(scopedKey);
  if (existing) return existing;

  // Production: call ServiceNow with a workload identity/OAuth token and map only
  // an allowlisted incident schema. Do not forward arbitrary agent-generated JSON.
  const incidentId = `INC-DEMO-${String(createdIncidents.size + 1).padStart(4, "0")}`;
  createdIncidents.set(scopedKey, incidentId);
  return incidentId;
}

export async function incidentExists(tenantId: string, incidentId: string): Promise<boolean> {
  return Array.from(createdIncidents.entries()).some(
    ([key, value]) => key.startsWith(`${tenantId}:`) && value === incidentId
  );
}
