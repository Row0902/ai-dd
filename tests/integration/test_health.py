"""Integration tests for the health endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from config.settings import AppSettings
from main import create_app


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_200_ok(self) -> None:
        """GET /health returns 200 with status ok."""
        app = create_app(AppSettings(DATABASE_URL="memory://"))
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["database"] == "up"

    def test_health_does_not_require_auth(self) -> None:
        """GET /health is accessible without Authorization header."""
        app = create_app(AppSettings(DATABASE_URL="memory://"))
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200
