"""Tests for SQLFavoriteRepository using in-memory SQLite."""

from __future__ import annotations

import pytest

from infrastructure.persistence.session import create_engine_from_url, create_tables
from infrastructure.persistence.sql_favorite_repository import SQLFavoriteRepository


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
    """Provide an SQLFavoriteRepository bound to the test session."""
    return SQLFavoriteRepository(db_session)


class TestSQLFavoriteRepositoryAdd:
    """Tests for add() method."""

    async def test_add_persists_favorite(self, repo):
        """add() should persist a user-book favorite."""
        await repo.add("u1", "b1")
        result = await repo.list_by_user("u1")
        assert result == ["b1"]

    async def test_add_is_idempotent(self, repo):
        """add() should not error when adding the same favorite twice."""
        await repo.add("u1", "b1")
        await repo.add("u1", "b1")
        result = await repo.list_by_user("u1")
        assert len(result) == 1


class TestSQLFavoriteRepositoryRemove:
    """Tests for remove() method."""

    async def test_remove_deletes_favorite(self, repo):
        """remove() should delete the favorite."""
        await repo.add("u1", "b1")
        await repo.remove("u1", "b1")
        assert await repo.list_by_user("u1") == []

    async def test_remove_is_idempotent(self, repo):
        """remove() should not error when removing a nonexistent favorite."""
        await repo.remove("u1", "b1")
        assert await repo.list_by_user("u1") == []


class TestSQLFavoriteRepositoryListByUser:
    """Tests for list_by_user() method."""

    async def test_list_by_user_returns_book_ids(self, repo):
        """list_by_user returns book IDs for the given user."""
        await repo.add("u1", "b1")
        await repo.add("u1", "b2")
        await repo.add("u2", "b3")
        result = await repo.list_by_user("u1")
        assert set(result) == {"b1", "b2"}

    async def test_list_by_user_empty(self, repo):
        """list_by_user returns empty list when no favorites exist."""
        assert await repo.list_by_user("nobody") == []

    async def test_list_by_user_reverse_chronological(self, repo):
        """list_by_user returns results ordered by added_at DESC."""
        await repo.add("u1", "b1")
        await repo.add("u1", "b2")
        await repo.add("u1", "b3")
        result = await repo.list_by_user("u1")
        assert len(result) == 3
        # b3 was added last, so it should be first
        assert result[0] == "b3"
        assert result[-1] == "b1"
