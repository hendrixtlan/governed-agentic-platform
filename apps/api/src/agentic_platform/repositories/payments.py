from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from agentic_platform.config import get_settings
from agentic_platform.graph.state import EvidenceItem


class PaymentRepository:
    def __init__(self):
        settings = get_settings()
        self.max_rows = settings.max_sql_rows
        self.session_factory = None
        if settings.database_url:
            engine = create_async_engine(settings.database_url, pool_pre_ping=True)
            self.session_factory = async_sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )

    async def get_recent_failures(
        self,
        *,
        tenant_id: str,
        subject: str,
    ) -> list[EvidenceItem]:
        if self.session_factory is None or get_settings().app_mode == "mock":
            return [
                {
                    "source": "payments",
                    "reference": "aggregate:last_24h",
                    "summary": (
                        f"{subject}: 27% payment failure rate in the last 24h; "
                        "dominant error=GATEWAY_TIMEOUT."
                    ),
                }
            ]

        # The LLM never writes this SQL. Tenant identity comes from ExecutionContext.
        stmt = text(
            """
            SELECT payment_id, customer_id, status, error_code, created_at
            FROM payments
            WHERE tenant_id = :tenant_id
              AND customer_id = :customer_id
              AND status = 'FAILED'
              AND created_at >= NOW() - INTERVAL '24 hours'
            ORDER BY created_at DESC
            LIMIT :row_limit
            """
        )
        params = {
            "tenant_id": tenant_id,
            "customer_id": subject,
            "row_limit": self.max_rows,
        }
        async with self.session_factory() as session:
            result = await session.execute(stmt, params)
            rows = result.mappings().all()
        return [
            {
                "source": "payments",
                "reference": str(row["payment_id"]),
                "summary": (
                    f"status={row['status']}; error={row['error_code']}; "
                    f"created_at={row['created_at']}"
                ),
            }
            for row in rows
        ]


payments = PaymentRepository()
