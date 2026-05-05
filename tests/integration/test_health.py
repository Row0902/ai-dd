"""Integration tests for the health endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.dependencies import get_book_repo
from config.settings import AppSettings
from main import create_app


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_200_ok(self) -> None:
        """GET /health returns 200 with status ok when DB is reachable."""
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

    def test_health_returns_503_when_db_unreachable(self) -> None:
        """GET /health returns 503 when the repository probe fails."""
        app = create_app(AppSettings(DATABASE_URL="memory://"))

        class BrokenRepo:
            """Repository stub that always fails."""

            async def list(self, *args, **kwargs):
                raise RuntimeError("connection lost")

        def get_broken_repo():
            return BrokenRepo()

        app.dependency_overrides[get_book_repo] = get_broken_repo
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 503
        body = resp.json()
        assert body["status"] == "error"
        assert body["database"] == "down"
