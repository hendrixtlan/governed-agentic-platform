# Contributing

1. Create a branch per capability or workflow change.
2. Keep model-driven decisions typed and narrow.
3. Do not add tenant IDs or credentials to model tool schemas.
4. Add unit tests for policy and graph routing changes.
5. Add security tests for every new data source or mutation.
6. Add contract tests for enterprise adapters.
7. Keep sensitive payloads out of logs and fixtures.
8. Run `make test` and `make lint` before opening a pull request.
