"""HTTP characterization tests for the books API.

These tests validate the end-to-end wiring: FastAPI endpoints -> use cases ->
repository adapter.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.dependencies import get_rate_limiter
from config.settings import AppSettings
from infrastructure.auth.jwt_token_service import JwtTokenService
from infrastructure.rate_limiting.noop_rate_limiter import NoOpRateLimiter
from main import create_app

TEST_SECRET = "test-secret-key-at-least-32-chars-long"


def _settings() -> AppSettings:
    """Create test application settings.

    Returns:
        AppSettings configured for testing.
    """
    return AppSettings(DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET)


def _client() -> TestClient:
    """Create a TestClient with in-memory repository.

    Returns:
        Configured TestClient instance.
    """
    app = create_app(_settings())
    app.dependency_overrides[get_rate_limiter] = lambda: NoOpRateLimiter()
    return TestClient(app)


def _auth_headers() -> dict[str, str]:
    """Create Authorization headers for a standard test user.

    Returns:
        Dict with Authorization Bearer header.
    """
    token_service = JwtTokenService(TEST_SECRET)
    token = token_service.generate("test-user-id", "user")
    return {"Authorization": f"Bearer {token}"}


class TestBooksApi:
    """Characterization tests for current HTTP behavior."""

    def test_list_books_empty(self) -> None:
        """GET /books returns empty list when no data exists."""
        client = _client()
        resp = client.get("/books", headers=_auth_headers())
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_then_get_then_list(self) -> None:
        """POST then GET by id then GET list returns consistent data."""
        client = _client()
        headers = _auth_headers()

        payload = {
            "name": "Clean Code",
            "author": "Robert C. Martin",
            "description": "A Handbook of Agile Software Craftsmanship",
            "url": "https://example.com/clean-code",
            "content": "Chapter 1",
        }
        created = client.post("/books", json=payload, headers=headers)
        assert created.status_code == 201
        body = created.json()
        assert body["id"]
        assert body["name"] == payload["name"]

        got = client.get(f"/books/{body['id']}", headers=headers)
        assert got.status_code == 200
        assert got.json() == body

        listed = client.get("/books", headers=headers)
        assert listed.status_code == 200
        assert listed.json() == [body]

    def test_get_missing_is_404(self) -> None:
        """GET /books/{id} returns 404 when missing."""
        client = _client()
        resp = client.get("/books/missing", headers=_auth_headers())
        assert resp.status_code == 404
        assert resp.json() == {"detail": "Not found"}

    def test_search_by_name_is_case_insensitive_substring(self) -> None:
        """GET /books/by-name/{name} performs case-insensitive substring search."""
        client = _client()
        headers = _auth_headers()
        client.post("/books", json={"name": "Clean Code"}, headers=headers)
        client.post("/books", json={"name": "The Clean Coder"}, headers=headers)
        client.post("/books", json={"name": "DDD"}, headers=headers)

        resp = client.get("/books/by-name/cLeAn", headers=headers)
        assert resp.status_code == 200
        names = sorted([b["name"] for b in resp.json()])
        assert names == ["Clean Code", "The Clean Coder"]

    def test_put_is_full_replace(self) -> None:
        """PUT /books/{id} is a full replacement (unspecified fields reset)."""
        client = _client()
        headers = _auth_headers()

        created = client.post(
            "/books",
            json={
                "name": "Old",
                "author": "Old Author",
                "description": "Old desc",
                "url": "https://example.com/old",
                "content": "old-content",
            },
            headers=headers,
        ).json()

        replaced = client.put(
            f"/books/{created['id']}", json={"name": "New"}, headers=headers
        )
        assert replaced.status_code == 200
        body = replaced.json()
        assert body["id"] == created["id"]
        assert body["name"] == "New"
        assert body["author"] == ""
        assert body["description"] == ""
        assert body["url"] == ""
        assert body["content"] == ""

    def test_delete_returns_204(self) -> None:
        """DELETE returns 204 with no body."""
        client = _client()
        headers = _auth_headers()
        created = client.post("/books", json={"name": "X"}, headers=headers).json()

        resp = client.delete(f"/books/{created['id']}", headers=headers)
        assert resp.status_code == 204

        missing = client.get(f"/books/{created['id']}", headers=headers)
        assert missing.status_code == 404

    def test_post_empty_name_returns_422(self) -> None:
        """POST /books rejects empty name with 422."""
        client = _client()
        resp = client.post(
            "/books",
            json={"name": "", "author": "Bob", "url": "https://example.com"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 422

    def test_post_whitespace_name_returns_422(self) -> None:
        """POST /books rejects whitespace-only name with 422."""
        client = _client()
        resp = client.post("/books", json={"name": "   "}, headers=_auth_headers())
        assert resp.status_code == 422

    def test_post_malformed_url_returns_422(self) -> None:
        """POST /books rejects malformed URL with 422."""
        client = _client()
        resp = client.post(
            "/books",
            json={"name": "Book", "url": "not-a-url"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 422

    def test_put_empty_name_returns_422(self) -> None:
        """PUT /books rejects empty name with 422."""
        client = _client()
        headers = _auth_headers()
        created = client.post("/books", json={"name": "Old"}, headers=headers).json()
        resp = client.put(
            f"/books/{created['id']}",
            json={"name": "", "author": "Bob"},
            headers=headers,
        )
        assert resp.status_code == 422

    def test_get_books_without_auth_returns_401(self) -> None:
        """GET /books without auth returns 401."""
        client = _client()
        resp = client.get("/books")
        assert resp.status_code == 401

    def test_post_books_without_auth_returns_401(self) -> None:
        """POST /books without auth returns 401."""
        client = _client()
        resp = client.post("/books", json={"name": "X"})
        assert resp.status_code == 401


class TestBooksApiPagination:
    """Tests for pagination query parameters on GET /books."""

    def _create_books(self, client: TestClient, count: int) -> list[dict]:
        """Create multiple books and return their response bodies."""
        headers = _auth_headers()
        books = []
        for i in range(count):
            resp = client.post(
                "/books", json={"name": f"Book {i:02d}"}, headers=headers
            )
            assert resp.status_code == 201
            books.append(resp.json())
        return books

    def test_list_books_default_pagination(self) -> None:
        """GET /books should accept limit and offset query params."""
        client = _client()
        self._create_books(client, 3)
        resp = client.get("/books", headers=_auth_headers())
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_list_books_with_limit(self) -> None:
        """GET /books?limit=2 should return at most 2 books."""
        client = _client()
        self._create_books(client, 5)
        resp = client.get("/books?limit=2", headers=_auth_headers())
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_books_with_offset(self) -> None:
        """GET /books?offset=2 should skip first 2 books."""
        client = _client()
        self._create_books(client, 5)
        resp = client.get("/books?offset=2", headers=_auth_headers())
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 3

    def test_list_books_with_limit_and_offset(self) -> None:
        """GET /books?limit=2&offset=1 should return books 1-2."""
        client = _client()
        self._create_books(client, 5)
        resp = client.get("/books?limit=2&offset=1", headers=_auth_headers())
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2

    def test_list_books_limit_validation(self) -> None:
        """GET /books?limit=0 should return 422 (ge=1 constraint)."""
        client = _client()
        resp = client.get("/books?limit=0", headers=_auth_headers())
        assert resp.status_code == 422

    def test_list_books_offset_validation(self) -> None:
        """GET /books?offset=-1 should return 422 (ge=0 constraint)."""
        client = _client()
        resp = client.get("/books?offset=-1", headers=_auth_headers())
        assert resp.status_code == 422
