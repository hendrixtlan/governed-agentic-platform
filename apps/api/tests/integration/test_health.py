from fastapi.testclient import TestClient

from agentic_platform.main import app


def test_health():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
