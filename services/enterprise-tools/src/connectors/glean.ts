import { Evidence } from "../types.js";

export async function searchKnowledge(tenantId: string, query: string): Promise<Evidence[]> {
  return [{
    source: "glean",
    reference: "runbook:payment-gateway",
    summary: `Authorized knowledge result for tenant ${tenantId}: validate gateway health, compare processor error rates, and follow controlled failover procedure.`
  }];
}
