# Security Model

## Security invariant

**A model decision can request a capability; it cannot grant itself access to that capability.**

## Controls

### Identity

Production must use validated OIDC/JWT identity. The included header-based authentication exists only for local demonstration.

### Tenant isolation

- Tenant identity comes from trusted authentication/authorization context.
- Request bodies and model outputs cannot set tenant identity.
- Every repository/adapter receives tenant context from `ExecutionContext`.
- Workflow resume checks tenant ownership before loading/resuming state.
- Checkpoint and cache keys must be tenant-safe.

### SQL

The default payment capability is a repository method, not arbitrary text-to-SQL.

Controls:

- parameterized SQL;
- fixed table/column surface;
- trusted tenant predicate;
- row limit;
- read-only database identity in production;
- timeout and resource limits.

If text-to-SQL is added later, require AST parsing, statement allowlists, table/column allowlists, tenant enforcement and query-cost limits before execution.

### Prompt injection

Retrieved enterprise content is **data, not instructions**. Model prompts tell the model to ignore instructions embedded in evidence. This is not sufficient by itself; capability authorization remains deterministic and downstream adapters never accept credentials, tenant IDs or unrestricted executable commands from the model.

### Actions

Write operations are separate from reads. Sensitive actions require explicit approval and re-authorization immediately before mutation.

### Secrets

Use workload identities and AWS Secrets Manager / equivalent. Never place credentials, OAuth tokens or database passwords in graph state or prompts.

### Logging

Log references and security decisions, not complete sensitive payloads.

## Threat cases covered by tests

- Tenant B cannot resume Tenant A workflow.
- Non-privileged role cannot execute ServiceNow mutation.
- Request body has no tenant override.
- SQL tenant filter is bound from trusted context.
- Model output cannot select arbitrary capability names due to typed schema.
