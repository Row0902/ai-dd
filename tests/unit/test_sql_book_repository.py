"""Tests for infrastructure.persistence.sql_book_repository.

Integration tests using in-memory SQLite.
"""

from __future__ import annotations

import pytest

from domain.entities import Book
from infrastructure.persistence.session import create_engine_from_url, create_tables
from infrastructure.persistence.sql_book_repository import SQLBookRepository


@pytest.fixture()
def db_session():
    """Provide a fresh in-memory SQLite session with tables created."""
    from infrastructure.persistence.session import get_session

    engine = create_engine_from_url("sqlite://")
    create_tables(engine)
    with get_session(engine) as session:
        yield session


@pytest.fixture()
def repo(db_session):
    """Provide an SQLBookRepository bound to the test session."""
    return SQLBookRepository(db_session)


class TestSQLBookRepositoryCreate:
    """Tests for create() method."""

    def test_create_persists_book(self, repo):
        """create() should persist a new book and return it."""
        book = Book(id="b1", name="Clean Code", author="Martin")
        created = repo.create(book)
        assert created.id == "b1"
        assert created.name == "Clean Code"
        assert created.author == "Martin"

    def test_create_generates_id_when_empty(self, repo):
        """create() should generate an id when one is not provided."""
        book = Book(id="", name="Test")
        created = repo.create(book)
        assert created.id != ""
        assert created.name == "Test"


class TestSQLBookRepositoryGet:
    """Tests for get() method."""

    def test_get_returns_book_when_found(self, repo):
        """get() should return the book when it exists."""
        repo.create(Book(id="b1", name="Test"))
        found = repo.get("b1")
        assert found is not None
        assert found.id == "b1"
        assert found.name == "Test"

    def test_get_returns_none_when_not_found(self, repo):
        """get() should return None for a nonexistent id."""
        assert repo.get("nonexistent") is None


class TestSQLBookRepositoryGetByName:
    """Tests for get_by_name() method."""

    def test_get_by_name_case_insensitive_substring(self, repo):
        """get_by_name should match case-insensitive substrings."""
        repo.create(Book(id="1", name="Clean Code"))
        repo.create(Book(id="2", name="The Clean Coder"))
        repo.create(Book(id="3", name="DDD"))
        results = repo.get_by_name("cLeAn")
        assert sorted(b.name for b in results) == ["Clean Code", "The Clean Coder"]

    def test_get_by_name_no_match(self, repo):
        """get_by_name should return empty list when nothing matches."""
        repo.create(Book(id="1", name="Clean Code"))
        assert repo.get_by_name("Python") == []


class TestSQLBookRepositoryList:
    """Tests for list() with pagination."""

    def _create_books(self, repo: SQLBookRepository, count: int):
        for i in range(count):
            repo.create(Book(id=f"b{i:02d}", name=f"Book {i:02d}"))

    def test_list_returns_all_when_fewer_than_limit(self, repo):
        """list() should return all books when fewer than limit exist."""
        self._create_books(repo, 5)
        assert len(repo.list()) == 5

    def test_list_limit_caps_results(self, repo):
        """list(limit=3) should return at most 3 books."""
        self._create_books(repo, 10)
        books = repo.list(limit=3)
        assert len(books) == 3

    def test_list_offset_skips_books(self, repo):
        """list(offset=2) should skip the first 2 books."""
        self._create_books(repo, 5)
        books = repo.list(offset=2)
        assert len(books) == 3

    def test_list_limit_and_offset_together(self, repo):
        """list(limit=2, offset=3) should return books at offset 3-4."""
        self._create_books(repo, 10)
        books = repo.list(limit=2, offset=3)
        assert len(books) == 2

    def test_list_offset_beyond_end_returns_empty(self, repo):
        """list(offset=100) on a 5-book repo should return empty list."""
        self._create_books(repo, 5)
        assert repo.list(offset=100) == []

    def test_list_default_limit_is_20(self, repo):
        """list() with default params should return up to 20 books."""
        self._create_books(repo, 25)
        assert len(repo.list()) == 20


class TestSQLBookRepositoryUpdate:
    """Tests for update() method."""

    def test_update_replaces_book(self, repo):
        """update() should replace the existing book data."""
        repo.create(Book(id="b1", name="Old"))
        updated = repo.update("b1", Book(id="ignored", name="New", author="A"))
        assert updated is not None
        assert updated.id == "b1"
        assert updated.name == "New"
        assert updated.author == "A"

    def test_update_returns_none_when_not_found(self, repo):
        """update() should return None for a nonexistent id."""
        assert repo.update("nope", Book(id="x", name="X")) is None


class TestSQLBookRepositoryDelete:
    """Tests for delete() method."""

    def test_delete_returns_true_when_found(self, repo):
        """delete() should return True and remove the book."""
        repo.create(Book(id="b1", name="To Delete"))
        assert repo.delete("b1") is True
        assert repo.get("b1") is None

    def test_delete_returns_false_when_not_found(self, repo):
        """delete() should return False for a nonexistent id."""
        assert repo.delete("nonexistent") is False
