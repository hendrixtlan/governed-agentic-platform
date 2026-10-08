import { Evidence } from "../types.js";

export async function getAccount(tenantId: string, subject: string): Promise<Evidence[]> {
  return [{
    source: "salesforce",
    reference: `account:${subject}`,
    summary: `${subject} is a strategic enterprise account in tenant ${tenantId}.`
  }];
}
