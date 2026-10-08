import { Request } from "express";

export function trustedTenant(req: Request): string {
  const tenant = req.header("X-Trusted-Tenant-Id");
  if (!tenant) throw new Error("Missing trusted tenant context");
  // Production: this service must authenticate the calling workload and must not
  // trust arbitrary public headers. mTLS/JWT/SigV4 + service policy are typical options.
  return tenant;
}
