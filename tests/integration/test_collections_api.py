"""Integration tests for the collections API endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.dependencies import _reset_repos
from config.settings import AppSettings
from infrastructure.auth.jwt_token_service import JwtTokenService
from main import create_app

TEST_SECRET = "test-secret-key-at-least-32-chars-long"


def _settings() -> AppSettings:
    """Create test application settings."""
    return AppSettings(DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET)


def _client() -> TestClient:
    """Create a TestClient with in-memory repository."""
    _reset_repos()
    return TestClient(create_app(_settings()))


def _user_headers(user_id: str = "test-user-id") -> dict[str, str]:
    """Create Authorization headers for a standard test user."""
    token_service = JwtTokenService(TEST_SECRET)
    token = token_service.generate(user_id, "user")
    return {"Authorization": f"Bearer {token}"}


def _admin_headers() -> dict[str, str]:
    """Create Authorization headers for an admin user."""
    token_service = JwtTokenService(TEST_SECRET)
    token = token_service.generate("admin-id", "admin")
    return {"Authorization": f"Bearer {token}"}


class TestCollectionsApi:
    """Integration tests for collection CRUD via HTTP."""

    def test_create_collection_returns_201(self) -> None:
        """POST /collections creates a collection and returns 201."""
        client = _client()
        resp = client.post(
            "/collections",
            json={"name": "My Books", "description": "Tech books"},
            headers=_user_headers(),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["id"]
        assert body["name"] == "My Books"
        assert body["description"] == "Tech books"
        assert body["owner_id"] == "test-user-id"
        assert body["book_ids"] == []

    def test_list_collections_user_sees_own(self) -> None:
        """GET /collections returns only the user's own collections."""
        client = _client()
        headers = _user_headers("user-1")
        client.post("/collections", json={"name": "Col1"}, headers=headers)
        client.post(
            "/collections",
            json={"name": "Col2"},
            headers=_user_headers("user-2"),
        )

        resp = client.get("/collections", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 1
        assert body[0]["name"] == "Col1"

    def test_list_collections_admin_sees_all(self) -> None:
        """GET /collections as admin returns all collections."""
        client = _client()
        client.post(
            "/collections",
            json={"name": "Col1"},
            headers=_user_headers("user-1"),
        )
        client.post(
            "/collections",
            json={"name": "Col2"},
            headers=_user_headers("user-2"),
        )

        resp = client.get("/collections", headers=_admin_headers())
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_delete_own_collection_returns_204(self) -> None:
        """DELETE /collections/{id} by owner returns 204."""
        client = _client()
        headers = _user_headers("user-1")
        created = client.post(
            "/collections", json={"name": "Mine"}, headers=headers
        ).json()

        resp = client.delete(f"/collections/{created['id']}", headers=headers)
        assert resp.status_code == 204

    def test_delete_other_users_collection_returns_403(self) -> None:
        """DELETE /collections/{id} by non-owner returns 403."""
        client = _client()
        owner_headers = _user_headers("owner")
        created = client.post(
            "/collections", json={"name": "Theirs"}, headers=owner_headers
        ).json()

        resp = client.delete(
            f"/collections/{created['id']}", headers=_user_headers("other")
        )
        assert resp.status_code == 403

    def test_admin_can_delete_any_collection(self) -> None:
        """DELETE /collections/{id} by admin returns 204."""
        client = _client()
        created = client.post(
            "/collections",
            json={"name": "Anyones"},
            headers=_user_headers("user-1"),
        ).json()

        resp = client.delete(
            f"/collections/{created['id']}", headers=_admin_headers()
        )
        assert resp.status_code == 204

    def test_delete_nonexistent_returns_404(self) -> None:
        """DELETE /collections/{id} for missing collection returns 404."""
        client = _client()
        resp = client.delete("/collections/missing", headers=_user_headers())
        assert resp.status_code == 404

    def test_create_without_auth_returns_401(self) -> None:
        """POST /collections without auth returns 401."""
        client = _client()
        resp = client.post("/collections", json={"name": "X"})
        assert resp.status_code == 401

    def test_list_without_auth_returns_401(self) -> None:
        """GET /collections without auth returns 401."""
        client = _client()
        resp = client.get("/collections")
        assert resp.status_code == 401

    def test_delete_without_auth_returns_401(self) -> None:
        """DELETE /collections/{id} without auth returns 401."""
        client = _client()
        resp = client.delete("/collections/anything")
        assert resp.status_code == 401
