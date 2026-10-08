import json
import logging
from typing import Any

logger = logging.getLogger("agentic-platform.audit")


def audit(event: str, **fields: Any) -> None:
    """Structured audit placeholder.

    Production should emit through OpenTelemetry / structured logging and apply
    redaction/data-classification rules before export.
    """
    logger.info(json.dumps({"event": event, **fields}, default=str))
