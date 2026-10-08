import express, { Request, Response } from "express";
import { trustedTenant } from "./policy.js";
import { getAccount } from "./connectors/salesforce.js";
import { createIncident, getIncidents, incidentExists } from "./connectors/servicenow.js";
import { getIssues } from "./connectors/jira.js";
import { searchKnowledge } from "./connectors/glean.js";
import { getServiceOwner } from "./connectors/oracleHcm.js";

const app = express();
app.use(express.json());

function wrap(
  fn: (tenant: string, value: string) => Promise<unknown>,
  param: string
) {
  return async (req: Request, res: Response) => {
    try {
      const tenant = trustedTenant(req);
      const value = String(req.query[param] ?? "");
      if (!value) return res.status(400).json({ error: `Missing ${param}` });
      return res.json({ evidence: await fn(tenant, value) });
    } catch (error) {
      return res.status(403).json({ error: error instanceof Error ? error.message : String(error) });
    }
  };
}

app.get("/health", (_req, res) => res.json({ status: "ok" }));
app.get("/salesforce/account", wrap(getAccount, "subject"));
app.get("/servicenow/incidents", wrap(getIncidents, "subject"));
app.get("/jira/issues", wrap(getIssues, "subject"));
app.get("/glean/search", wrap(searchKnowledge, "query"));
app.get("/oracle-hcm/owner", wrap(getServiceOwner, "subject"));

app.post("/servicenow/incidents", async (req: Request, res: Response) => {
  try {
    const tenant = trustedTenant(req);
    const idempotencyKey = req.header("Idempotency-Key");
    if (!idempotencyKey) return res.status(400).json({ error: "Missing Idempotency-Key" });

    const { title, description, priority } = req.body ?? {};
    if (!title || !description || !priority) {
      return res.status(400).json({ error: "title, description and priority are required" });
    }
    const incidentId = await createIncident(
      tenant,
      { title: String(title), description: String(description), priority: String(priority) },
      idempotencyKey
    );
    return res.status(201).json({ incident_id: incidentId });
  } catch (error) {
    return res.status(403).json({ error: error instanceof Error ? error.message : String(error) });
  }
});

app.get("/servicenow/incidents/:incidentId", async (req: Request, res: Response) => {
  try {
    const tenant = trustedTenant(req);
    const exists = await incidentExists(tenant, req.params.incidentId);
    if (!exists) return res.status(404).json({ exists: false });
    return res.json({ exists: true });
  } catch (error) {
    return res.status(403).json({ error: error instanceof Error ? error.message : String(error) });
  }
});

const port = Number(process.env.PORT ?? 8100);
app.listen(port, "0.0.0.0", () => {
  console.log(`enterprise-tools listening on ${port}`);
});
