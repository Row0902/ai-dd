"""HTTP characterization tests for the books API.

These tests validate the end-to-end wiring: FastAPI endpoints -> use cases ->
repository adapter.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from config.settings import AppSettings
from main import create_app


def _client() -> TestClient:
    """Create a TestClient with in-memory repository."""
    app = create_app(AppSettings(DATABASE_URL="memory://"))
    return TestClient(app)


class TestBooksApi:
    """Characterization tests for current HTTP behavior."""

    def test_list_books_empty(self) -> None:
        """GET /books returns empty list when no data exists."""
        client = _client()
        resp = client.get("/books")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_then_get_then_list(self) -> None:
        """POST then GET by id then GET list returns consistent data."""
        client = _client()

        payload = {
            "name": "Clean Code",
            "author": "Robert C. Martin",
            "description": "A Handbook of Agile Software Craftsmanship",
            "url": "https://example.com/clean-code",
            "content": "Chapter 1",
        }
        created = client.post("/books", json=payload)
        assert created.status_code == 200
        body = created.json()
        assert body["id"]
        assert body["name"] == payload["name"]

        got = client.get(f"/books/{body['id']}")
        assert got.status_code == 200
        assert got.json() == body

        listed = client.get("/books")
        assert listed.status_code == 200
        assert listed.json() == [body]

    def test_get_missing_is_404(self) -> None:
        """GET /books/{id} returns 404 when missing."""
        client = _client()
        resp = client.get("/books/missing")
        assert resp.status_code == 404
        assert resp.json() == {"detail": "Not found"}

    def test_search_by_name_is_case_insensitive_substring(self) -> None:
        """GET /books/by-name/{name} performs case-insensitive substring search."""
        client = _client()
        client.post("/books", json={"name": "Clean Code"})
        client.post("/books", json={"name": "The Clean Coder"})
        client.post("/books", json={"name": "DDD"})

        resp = client.get("/books/by-name/cLeAn")
        assert resp.status_code == 200
        names = sorted([b["name"] for b in resp.json()])
        assert names == ["Clean Code", "The Clean Coder"]

    def test_put_is_full_replace(self) -> None:
        """PUT /books/{id} is a full replacement (unspecified fields reset)."""
        client = _client()

        created = client.post(
            "/books",
            json={
                "name": "Old",
                "author": "Old Author",
                "description": "Old desc",
                "url": "https://example.com/old",
                "content": "old-content",
            },
        ).json()

        replaced = client.put(f"/books/{created['id']}", json={"name": "New"})
        assert replaced.status_code == 200
        body = replaced.json()
        assert body["id"] == created["id"]
        assert body["name"] == "New"
        assert body["author"] == ""
        assert body["description"] == ""
        assert body["url"] == ""
        assert body["content"] == ""

    def test_delete_returns_deleted_book(self) -> None:
        """DELETE returns the deleted book object."""
        client = _client()
        created = client.post("/books", json={"name": "X"}).json()

        resp = client.delete(f"/books/{created['id']}")
        assert resp.status_code == 200
        assert resp.json() == {"deleted": created}

        missing = client.get(f"/books/{created['id']}")
        assert missing.status_code == 404

    def test_post_empty_name_returns_422(self) -> None:
        """POST /books rejects empty name with 422."""
        client = _client()
        resp = client.post(
            "/books",
            json={"name": "", "author": "Bob", "url": "https://example.com"},
        )
        assert resp.status_code == 422

    def test_post_whitespace_name_returns_422(self) -> None:
        """POST /books rejects whitespace-only name with 422."""
        client = _client()
        resp = client.post("/books", json={"name": "   "})
        assert resp.status_code == 422

    def test_post_malformed_url_returns_422(self) -> None:
        """POST /books rejects malformed URL with 422."""
        client = _client()
        resp = client.post("/books", json={"name": "Book", "url": "not-a-url"})
        assert resp.status_code == 422

    def test_put_empty_name_returns_422(self) -> None:
        """PUT /books rejects empty name with 422."""
        client = _client()
        created = client.post("/books", json={"name": "Old"}).json()
        resp = client.put(f"/books/{created['id']}", json={"name": "", "author": "Bob"})
        assert resp.status_code == 422


class TestBooksApiPagination:
    """Tests for pagination query parameters on GET /books."""

    def _create_books(self, client: TestClient, count: int) -> list[dict]:
        """Create multiple books and return their response bodies."""
        books = []
        for i in range(count):
            resp = client.post("/books", json={"name": f"Book {i:02d}"})
            assert resp.status_code == 200
            books.append(resp.json())
        return books

    def test_list_books_default_pagination(self) -> None:
        """GET /books should accept limit and offset query params."""
        client = _client()
        self._create_books(client, 3)
        resp = client.get("/books")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_list_books_with_limit(self) -> None:
        """GET /books?limit=2 should return at most 2 books."""
        client = _client()
        self._create_books(client, 5)
        resp = client.get("/books?limit=2")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_books_with_offset(self) -> None:
        """GET /books?offset=2 should skip first 2 books."""
        client = _client()
        self._create_books(client, 5)
        resp = client.get("/books?offset=2")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 3

    def test_list_books_with_limit_and_offset(self) -> None:
        """GET /books?limit=2&offset=1 should return books 1-2."""
        client = _client()
        self._create_books(client, 5)
        resp = client.get("/books?limit=2&offset=1")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2

    def test_list_books_limit_validation(self) -> None:
        """GET /books?limit=0 should return 422 (ge=1 constraint)."""
        client = _client()
        resp = client.get("/books?limit=0")
        assert resp.status_code == 422

    def test_list_books_offset_validation(self) -> None:
        """GET /books?offset=-1 should return 422 (ge=0 constraint)."""
        client = _client()
        resp = client.get("/books?offset=-1")
        assert resp.status_code == 422
