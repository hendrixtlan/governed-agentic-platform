.PHONY: api web tools test lint compose

api:
	cd apps/api && uvicorn agentic_platform.main:app --reload --port 8000

web:
	cd apps/web && npm run dev

tools:
	cd services/enterprise-tools && npm run dev

test:
	cd apps/api && pytest -q

lint:
	cd apps/api && ruff check src tests

compose:
	docker compose up --build
