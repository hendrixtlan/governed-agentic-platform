#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"

curl -sS -X POST "$API_URL/v1/investigations" \
  -H 'Content-Type: application/json' \
  -H 'X-User-Id: jose' \
  -H 'X-Tenant-Id: ACME' \
  -H 'X-Roles: analyst,ops_manager' \
  -d '{
    "question":"Why are payments failing, are there active incidents, and what should we do?",
    "subject":"customer-123"
  }' | python -m json.tool
