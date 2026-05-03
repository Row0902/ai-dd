"""HTTP characterization tests for the books API.

These tests validate the end-to-end wiring: FastAPI endpoints -> use cases ->
JSON repository adapter.
"""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from main import create_app


def _client_with_data_file(tmp_path: Path) -> TestClient:
    app = create_app(tmp_path / "library.json")
    return TestClient(app)


class TestBooksApi:
    """Characterization tests for current HTTP behavior."""

    def test_list_books_empty(self, tmp_path: Path) -> None:
        """GET /books returns empty list when no data exists."""
        client = _client_with_data_file(tmp_path)
        resp = client.get("/books")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_then_get_then_list(self, tmp_path: Path) -> None:
        """POST then GET by id then GET list returns consistent data."""
        client = _client_with_data_file(tmp_path)

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

    def test_get_missing_is_404(self, tmp_path: Path) -> None:
        """GET /books/{id} returns 404 when missing."""
        client = _client_with_data_file(tmp_path)
        resp = client.get("/books/missing")
        assert resp.status_code == 404
        assert resp.json() == {"detail": "Not found"}

    def test_search_by_name_is_case_insensitive_substring(self, tmp_path: Path) -> None:
        """GET /books/by-name/{name} performs case-insensitive substring search."""
        client = _client_with_data_file(tmp_path)
        client.post("/books", json={"name": "Clean Code"})
        client.post("/books", json={"name": "The Clean Coder"})
        client.post("/books", json={"name": "DDD"})

        resp = client.get("/books/by-name/cLeAn")
        assert resp.status_code == 200
        names = sorted([b["name"] for b in resp.json()])
        assert names == ["Clean Code", "The Clean Coder"]

    def test_put_is_full_replace(self, tmp_path: Path) -> None:
        """PUT /books/{id} is a full replacement (unspecified fields reset)."""
        client = _client_with_data_file(tmp_path)

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

    def test_delete_returns_deleted_book(self, tmp_path: Path) -> None:
        """DELETE returns the deleted book object."""
        client = _client_with_data_file(tmp_path)
        created = client.post("/books", json={"name": "X"}).json()

        resp = client.delete(f"/books/{created['id']}")
        assert resp.status_code == 200
        assert resp.json() == {"deleted": created}

        missing = client.get(f"/books/{created['id']}")
        assert missing.status_code == 404
