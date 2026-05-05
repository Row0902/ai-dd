"""Tests for infrastructure.persistence.sql_book_repository.

Integration tests using in-memory SQLite with async sessions.
"""

from __future__ import annotations

import pytest

from domain.entities import Book
from infrastructure.persistence.session import create_engine_from_url, create_tables
from infrastructure.persistence.sql_book_repository import SQLBookRepository


@pytest.fixture()
async def db_session():
    """Provide a fresh in-memory async SQLite session with tables created."""
    from infrastructure.persistence.session import get_session

    engine = create_engine_from_url("sqlite://")
    await create_tables(engine)
    async with get_session(engine) as session:
        yield session
    await engine.dispose()


@pytest.fixture()
async def repo(db_session):
    """Provide an SQLBookRepository bound to the test session."""
    return SQLBookRepository(db_session)


class TestSQLBookRepositoryCreate:
    """Tests for create() method."""

    async def test_create_persists_book(self, repo):
        """create() should persist a new book and return it."""
        book = Book(id="b1", name="Clean Code", author="Martin")
        created = await repo.create(book)
        assert created.id == "b1"
        assert created.name == "Clean Code"
        assert created.author == "Martin"

    async def test_create_generates_id_when_empty(self, repo):
        """create() should generate an id when one is not provided."""
        book = Book(id="", name="Test")
        created = await repo.create(book)
        assert created.id != ""
        assert created.name == "Test"


class TestSQLBookRepositoryGet:
    """Tests for get() method."""

    async def test_get_returns_book_when_found(self, repo):
        """get() should return the book when it exists."""
        await repo.create(Book(id="b1", name="Test"))
        found = await repo.get("b1")
        assert found is not None
        assert found.id == "b1"
        assert found.name == "Test"

    async def test_get_returns_none_when_not_found(self, repo):
        """get() should return None for a nonexistent id."""
        assert await repo.get("nonexistent") is None


class TestSQLBookRepositoryGetByName:
    """Tests for get_by_name() method."""

    async def test_get_by_name_case_insensitive_substring(self, repo):
        """get_by_name should match case-insensitive substrings."""
        await repo.create(Book(id="1", name="Clean Code"))
        await repo.create(Book(id="2", name="The Clean Coder"))
        await repo.create(Book(id="3", name="DDD"))
        results = await repo.get_by_name("cLeAn")
        assert sorted(b.name for b in results) == ["Clean Code", "The Clean Coder"]

    async def test_get_by_name_no_match(self, repo):
        """get_by_name should return empty list when nothing matches."""
        await repo.create(Book(id="1", name="Clean Code"))
        assert await repo.get_by_name("Python") == []


class TestSQLBookRepositoryList:
    """Tests for list() with pagination."""

    async def _create_books(self, repo: SQLBookRepository, count: int):
        for i in range(count):
            await repo.create(Book(id=f"b{i:02d}", name=f"Book {i:02d}"))

    async def test_list_returns_all_when_fewer_than_limit(self, repo):
        """list() should return all books when fewer than limit exist."""
        await self._create_books(repo, 5)
        assert len(await repo.list()) == 5

    async def test_list_limit_caps_results(self, repo):
        """list(limit=3) should return at most 3 books."""
        await self._create_books(repo, 10)
        books = await repo.list(limit=3)
        assert len(books) == 3

    async def test_list_offset_skips_books(self, repo):
        """list(offset=2) should skip the first 2 books."""
        await self._create_books(repo, 5)
        books = await repo.list(offset=2)
        assert len(books) == 3

    async def test_list_limit_and_offset_together(self, repo):
        """list(limit=2, offset=3) should return books at offset 3-4."""
        await self._create_books(repo, 10)
        books = await repo.list(limit=2, offset=3)
        assert len(books) == 2

    async def test_list_offset_beyond_end_returns_empty(self, repo):
        """list(offset=100) on a 5-book repo should return empty list."""
        await self._create_books(repo, 5)
        assert await repo.list(offset=100) == []

    async def test_list_default_limit_is_20(self, repo):
        """list() with default params should return up to 20 books."""
        await self._create_books(repo, 25)
        assert len(await repo.list()) == 20


class TestSQLBookRepositoryUpdate:
    """Tests for update() method."""

    async def test_update_replaces_book(self, repo):
        """update() should replace the existing book data."""
        await repo.create(Book(id="b1", name="Old"))
        updated = await repo.update("b1", Book(id="ignored", name="New", author="A"))
        assert updated is not None
        assert updated.id == "b1"
        assert updated.name == "New"
        assert updated.author == "A"

    async def test_update_returns_none_when_not_found(self, repo):
        """update() should return None for a nonexistent id."""
        assert await repo.update("nope", Book(id="x", name="X")) is None


class TestSQLBookRepositoryDelete:
    """Tests for delete() method."""

    async def test_delete_returns_true_when_found(self, repo):
        """delete() should return True and remove the book."""
        await repo.create(Book(id="b1", name="To Delete"))
        assert await repo.delete("b1") is True
        assert await repo.get("b1") is None

    async def test_delete_returns_false_when_not_found(self, repo):
        """delete() should return False for a nonexistent id."""
        assert await repo.delete("nonexistent") is False
