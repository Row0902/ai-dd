"""Integration tests for the favorites API endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.dependencies import _reset_repos, get_rate_limiter
from config.settings import AppSettings
from infrastructure.auth.jwt_token_service import JwtTokenService
from infrastructure.rate_limiting.noop_rate_limiter import NoOpRateLimiter
from main import create_app

TEST_SECRET = "test-secret-key-at-least-32-chars-long"


def _settings() -> AppSettings:
    """Create test application settings."""
    return AppSettings(DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET)


def _client() -> TestClient:
    """Create a TestClient with in-memory repository."""
    _reset_repos()
    app = create_app(_settings())
    app.dependency_overrides[get_rate_limiter] = lambda: NoOpRateLimiter()
    return TestClient(app)


def _user_headers(user_id: str = "test-user-id") -> dict[str, str]:
    """Create Authorization headers for a standard test user."""
    token_service = JwtTokenService(TEST_SECRET)
    token = token_service.generate(user_id, "user")
    return {"Authorization": f"Bearer {token}"}


def _create_book(client: TestClient, name: str = "Test Book") -> str:
    """Helper: create a book and return its id."""
    resp = client.post(
        "/books",
        json={"name": name},
        headers=_user_headers(),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


class TestFavoritesApi:
    """Integration tests for favorites CRUD via HTTP."""

    def test_add_favorite_returns_201(self) -> None:
        """POST /favorites/{book_id} adds a favorite and returns 201."""
        client = _client()
        book_id = _create_book(client)
        resp = client.post(f"/favorites/{book_id}", headers=_user_headers())
        assert resp.status_code == 201

    def test_add_favorite_is_idempotent(self) -> None:
        """POST /favorites/{book_id} twice returns 201 both times."""
        client = _client()
        book_id = _create_book(client)
        headers = _user_headers()
        resp1 = client.post(f"/favorites/{book_id}", headers=headers)
        resp2 = client.post(f"/favorites/{book_id}", headers=headers)
        assert resp1.status_code == 201
        assert resp2.status_code == 201

    def test_list_favorites_returns_book_ids(self) -> None:
        """GET /favorites returns the user's favorite book IDs."""
        client = _client()
        headers = _user_headers()
        book_id = _create_book(client)
        client.post(f"/favorites/{book_id}", headers=headers)

        resp = client.get("/favorites", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == [book_id]

    def test_remove_favorite_returns_204(self) -> None:
        """DELETE /favorites/{book_id} removes a favorite and returns 204."""
        client = _client()
        headers = _user_headers()
        book_id = _create_book(client)
        client.post(f"/favorites/{book_id}", headers=headers)

        resp = client.delete(f"/favorites/{book_id}", headers=headers)
        assert resp.status_code == 204

        # Verify removed
        listed = client.get("/favorites", headers=headers)
        assert listed.json() == []

    def test_remove_favorite_is_idempotent(self) -> None:
        """DELETE /favorites/{book_id} for nonexistent returns 204."""
        client = _client()
        resp = client.delete("/favorites/nonexistent", headers=_user_headers())
        assert resp.status_code == 204

    def test_add_without_auth_returns_401(self) -> None:
        """POST /favorites/{book_id} without auth returns 401."""
        client = _client()
        resp = client.post("/favorites/anything")
        assert resp.status_code == 401

    def test_list_without_auth_returns_401(self) -> None:
        """GET /favorites without auth returns 401."""
        client = _client()
        resp = client.get("/favorites")
        assert resp.status_code == 401

    def test_remove_without_auth_returns_401(self) -> None:
        """DELETE /favorites/{book_id} without auth returns 401."""
        client = _client()
        resp = client.delete("/favorites/anything")
        assert resp.status_code == 401
