# Engineering Roadmap

## Phase 1 — Reference vertical slice
- React investigation UI
- FastAPI identity/control boundary
- LangGraph stateful orchestration
- Governed TypeScript adapters
- Mock model mode + Bedrock mode
- Human approval interrupt/resume
- CI security/unit tests

## Phase 2 — Durable and observable
- PostgreSQL LangGraph checkpointer
- Durable workflow/tenant registry
- OpenTelemetry traces and redaction
- Per-tool retry/timeout/circuit-breaker policy
- SSE workflow progress to React

## Phase 3 — Enterprise governance
- OIDC/JWT integration
- Amazon Verified Permissions/Cedar or enterprise PDP
- AWS Secrets Manager/KMS
- source-system OAuth/service identities
- Glean ACL-preserving search
- governed RAG metadata filters

## Phase 4 — Scale and advanced workflows
- parallel evidence fan-out/fan-in
- reusable subgraphs by domain
- eval datasets and Bedrock quality gates
- workload cost controls
- production SLOs and runbooks
