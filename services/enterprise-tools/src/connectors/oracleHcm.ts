import { Evidence } from "../types.js";

export async function getServiceOwner(tenantId: string, subject: string): Promise<Evidence[]> {
  return [{
    source: "oracle_hcm",
    reference: "org:payments-platform",
    summary: `Payments Platform owns ${subject}. Only organization ownership is returned; sensitive HR attributes are excluded.`
  }];
}
