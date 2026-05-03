"""Unit tests for JsonBookRepository.

These tests exercise file persistence behavior using pytest's tmp_path.
"""

from __future__ import annotations

import json
from pathlib import Path

from domain.entities import Book
from infrastructure.json_book_repository import JsonBookRepository


def _repo(tmp_path: Path) -> JsonBookRepository:
    return JsonBookRepository(tmp_path / "library.json")


class TestJsonBookRepository:
    """Tests for JSON-backed repository."""

    def test_missing_file_is_empty(self, tmp_path: Path) -> None:
        """Missing file behaves like an empty library."""
        repo = _repo(tmp_path)
        assert repo.list() == []

    def test_create_assigns_id_when_missing(self, tmp_path: Path) -> None:
        """Create assigns a UUID hex id if the entity id is empty."""
        repo = _repo(tmp_path)
        created = repo.create(Book(id="", name="Clean Code"))
        assert created.id
        assert repo.get(created.id) == created

    def test_get_by_name_is_case_insensitive_substring(self, tmp_path: Path) -> None:
        """Search matches case-insensitive substrings in the name."""
        repo = _repo(tmp_path)
        repo.create(Book(id="", name="Clean Code"))
        repo.create(Book(id="", name="The Clean Coder"))
        repo.create(Book(id="", name="DDD"))
        res = repo.get_by_name("cLeAn")
        assert sorted([b.name for b in res]) == ["Clean Code", "The Clean Coder"]

    def test_update_replaces_full_representation(self, tmp_path: Path) -> None:
        """Update stores the passed book as a full replacement."""
        repo = _repo(tmp_path)
        created = repo.create(Book(id="", name="Old", author="a"))
        updated = repo.update(created.id, Book(id="ignored", name="New"))
        assert updated is not None
        assert updated.id == created.id
        assert updated.name == "New"
        assert updated.author == ""

    def test_delete_returns_true_only_when_found(self, tmp_path: Path) -> None:
        """Delete returns True when it deletes an existing book."""
        repo = _repo(tmp_path)
        created = repo.create(Book(id="", name="X"))
        assert repo.delete(created.id) is True
        assert repo.delete(created.id) is False

    def test_corrupt_json_is_treated_as_empty(self, tmp_path: Path) -> None:
        """Corrupt JSON is treated as empty to match monolith behavior."""
        path = tmp_path / "library.json"
        path.write_text("{not-json", encoding="utf-8")
        repo = JsonBookRepository(path)
        assert repo.list() == []

    def test_non_list_json_is_treated_as_empty(self, tmp_path: Path) -> None:
        """Non-list JSON (e.g., object) is treated as empty."""
        path = tmp_path / "library.json"
        path.write_text(json.dumps({"x": 1}), encoding="utf-8")
        repo = JsonBookRepository(path)
        assert repo.list() == []
