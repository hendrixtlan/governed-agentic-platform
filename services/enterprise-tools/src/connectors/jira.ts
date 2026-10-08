import { Evidence } from "../types.js";

export async function getIssues(tenantId: string, subject: string): Promise<Evidence[]> {
  return [{
    source: "jira",
    reference: "PAY-451",
    summary: `Timeout regression under investigation for ${subject}; tenant=${tenantId}.`
  }];
}
