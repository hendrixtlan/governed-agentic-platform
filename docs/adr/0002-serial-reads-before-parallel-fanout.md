# ADR 0002: Start with serial governed reads

## Status
Accepted for reference implementation

## Decision
The first graph executes selected read capabilities serially through a router.

## Rationale
This makes authorization, traces, checkpoint behavior and partial-failure semantics obvious. The production optimization path is parallel fan-out/fan-in for independent reads once per-tool timeouts, concurrency limits and merge semantics are specified.

## Future change
Use LangGraph `Send` or explicit parallel edges and retain reducers on `evidence`/`errors`.
