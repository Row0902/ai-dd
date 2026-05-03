"""Unit tests for JsonBookRepository.

These tests exercise file persistence behavior using pytest's tmp_path.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from domain.entities import Book
from domain.exceptions import DomainError
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


class TestDictToBook:
    """Tests for _dict_to_book raising DomainError on malformed data."""

    def test_missing_id_raises_domain_error(self) -> None:
        """A dict with no id field raises DomainError."""
        with pytest.raises(DomainError):
            JsonBookRepository._dict_to_book({"name": "Book"})

    def test_missing_name_raises_domain_error(self) -> None:
        """A dict with no name field raises DomainError."""
        with pytest.raises(DomainError):
            JsonBookRepository._dict_to_book({"id": "123"})

    def test_non_string_id_raises_domain_error(self) -> None:
        """A dict with non-string id raises DomainError."""
        with pytest.raises(DomainError):
            JsonBookRepository._dict_to_book({"id": 123, "name": "Book"})

    def test_non_string_name_raises_domain_error(self) -> None:
        """A dict with non-string name raises DomainError."""
        with pytest.raises(DomainError):
            JsonBookRepository._dict_to_book({"id": "123", "name": 42})

    def test_valid_dict_returns_book(self) -> None:
        """A well-formed dict returns a valid Book."""
        book = JsonBookRepository._dict_to_book(
            {"id": "abc", "name": "Clean Code", "author": "Bob"}
        )
        assert book.id == "abc"
        assert book.name == "Clean Code"
        assert book.author == "Bob"

    def test_malformed_entries_skipped_in_list(self, tmp_path: Path) -> None:
        """Malformed entries in JSON file are silently skipped during list."""
        path = tmp_path / "library.json"
        data = [
            {"id": "1", "name": "Good Book"},
            {"name": "Missing ID"},  # malformed — no id
            {"id": "2", "name": "Another Good Book"},
        ]
        path.write_text(json.dumps(data), encoding="utf-8")
        repo = JsonBookRepository(path)
        books = repo.list()
        assert len(books) == 2
        assert books[0].name == "Good Book"
        assert books[1].name == "Another Good Book"
