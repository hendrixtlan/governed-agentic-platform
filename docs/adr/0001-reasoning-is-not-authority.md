# ADR 0001: Separate reasoning from authority

## Status
Accepted

## Decision
LLM/LangGraph decisions may select a named capability, but identity, tenant context, authorization, credentials, data filters and mutation rights remain deterministic application concerns.

## Consequences
- Tenant ID is excluded from model tool arguments.
- Each tool call is authorized at invocation time.
- Mutations are re-authorized after human approval.
- Enterprise adapters expose narrow business capabilities instead of generic REST/SQL execution.
