"""Tests for SQLCollectionRepository using in-memory SQLite."""

from __future__ import annotations

import pytest

from domain.collections.entities import Collection
from infrastructure.persistence.session import create_engine_from_url, create_tables
from infrastructure.persistence.sql_collection_repository import SQLCollectionRepository


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
    """Provide an SQLCollectionRepository bound to the test session."""
    return SQLCollectionRepository(db_session)


class TestSQLCollectionRepositorySave:
    """Tests for save() method."""

    async def test_save_persists_collection(self, repo):
        """save() should persist a new collection and return it."""
        col = Collection(id="c1", name="My Books", owner_id="u1")
        saved = await repo.save(col)
        assert saved.id == "c1"
        assert saved.name == "My Books"
        assert saved.owner_id == "u1"

    async def test_save_updates_existing(self, repo):
        """save() should update an existing collection."""
        col = Collection(id="c1", name="Old", owner_id="u1")
        await repo.save(col)
        col.name = "New"
        updated = await repo.save(col)
        assert updated.name == "New"

    async def test_save_with_book_ids(self, repo):
        """save() should persist book_ids as JSON."""
        col = Collection(id="c1", name="Col", owner_id="u1", book_ids=["b1", "b2"])
        await repo.save(col)
        found = await repo.find_by_id("c1")
        assert found is not None
        assert found.book_ids == ["b1", "b2"]


class TestSQLCollectionRepositoryFindById:
    """Tests for find_by_id() method."""

    async def test_find_by_id_returns_collection(self, repo):
        """find_by_id returns the collection when it exists."""
        await repo.save(Collection(id="c1", name="Test", owner_id="u1"))
        found = await repo.find_by_id("c1")
        assert found is not None
        assert found.id == "c1"

    async def test_find_by_id_returns_none_when_missing(self, repo):
        """find_by_id returns None for nonexistent id."""
        assert await repo.find_by_id("missing") is None


class TestSQLCollectionRepositoryFindByOwnerId:
    """Tests for find_by_owner_id() method."""

    async def test_find_by_owner_id_returns_owned(self, repo):
        """find_by_owner_id returns only collections owned by that user."""
        await repo.save(Collection(id="c1", name="A", owner_id="u1"))
        await repo.save(Collection(id="c2", name="B", owner_id="u2"))
        await repo.save(Collection(id="c3", name="C", owner_id="u1"))
        results = await repo.find_by_owner_id("u1")
        assert len(results) == 2
        assert {c.id for c in results} == {"c1", "c3"}

    async def test_find_by_owner_id_empty(self, repo):
        """find_by_owner_id returns empty list when no matches."""
        assert await repo.find_by_owner_id("nobody") == []


class TestSQLCollectionRepositoryListAll:
    """Tests for list_all() method."""

    async def test_list_all_returns_everything(self, repo):
        """list_all returns all collections regardless of owner."""
        await repo.save(Collection(id="c1", name="A", owner_id="u1"))
        await repo.save(Collection(id="c2", name="B", owner_id="u2"))
        results = await repo.list_all()
        assert len(results) == 2

    async def test_list_all_empty(self, repo):
        """list_all returns empty list when nothing exists."""
        assert await repo.list_all() == []


class TestSQLCollectionRepositoryDelete:
    """Tests for delete() method."""

    async def test_delete_returns_true_when_found(self, repo):
        """Delete returns True and removes the collection."""
        await repo.save(Collection(id="c1", name="Test", owner_id="u1"))
        assert await repo.delete("c1") is True
        assert await repo.find_by_id("c1") is None

    async def test_delete_returns_false_when_not_found(self, repo):
        """Delete returns False for a nonexistent id."""
        assert await repo.delete("missing") is False
