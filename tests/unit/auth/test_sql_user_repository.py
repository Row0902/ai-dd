"""Tests for infrastructure.auth.sql_user_repository.

Integration tests using in-memory SQLite with async sessions.
"""

from __future__ import annotations

import pytest

from domain.auth.entities import User, UserRole
from infrastructure.persistence.session import create_engine_from_url, create_tables


@pytest.fixture()
async def db_session():
    """Provide a fresh in-memory async SQLite session with auth tables created."""
    from infrastructure.persistence.session import get_session

    engine = create_engine_from_url("sqlite://")
    # Import auth models so they register with SQLModel metadata
    import infrastructure.auth.sql_models  # noqa: F401
    await create_tables(engine)
    async with get_session(engine) as session:
        yield session
    await engine.dispose()


@pytest.fixture()
async def repo(db_session):
    """Provide an SQLUserRepository bound to the test session."""
    from infrastructure.auth.sql_user_repository import SQLUserRepository

    return SQLUserRepository(db_session)


class TestSQLUserRepositorySave:
    """Tests for save() method."""

    async def test_save_persists_user(self, repo):
        """save() should persist a new user and return it."""
        user = User(
            id="u1",
            email="alice@example.com",
            hashed_password="$2b$12$hashed",
            role=UserRole.USER,
        )
        saved = await repo.save(user)
        assert saved.id == "u1"
        assert saved.email == "alice@example.com"
        assert saved.role == UserRole.USER
        assert saved.is_active is True

    async def test_save_persists_admin_role(self, repo):
        """save() should persist admin role correctly."""
        user = User(
            id="u2",
            email="admin@example.com",
            hashed_password="$2b$12$hashed",
            role=UserRole.ADMIN,
        )
        saved = await repo.save(user)
        assert saved.role == UserRole.ADMIN


class TestSQLUserRepositoryFindByEmail:
    """Tests for find_by_email() method."""

    async def test_find_by_email_returns_user_when_found(self, repo):
        """find_by_email() should return the user when it exists."""
        user = User(
            id="u1",
            email="alice@example.com",
            hashed_password="$2b$12$hashed",
        )
        await repo.save(user)
        found = await repo.find_by_email("alice@example.com")
        assert found is not None
        assert found.id == "u1"
        assert found.email == "alice@example.com"

    async def test_find_by_email_returns_none_when_not_found(self, repo):
        """find_by_email() should return None for a nonexistent email."""
        assert await repo.find_by_email("nobody@example.com") is None


class TestSQLUserRepositoryFindById:
    """Tests for find_by_id() method."""

    async def test_find_by_id_returns_user_when_found(self, repo):
        """find_by_id() should return the user when it exists."""
        user = User(
            id="u1",
            email="alice@example.com",
            hashed_password="$2b$12$hashed",
        )
        await repo.save(user)
        found = await repo.find_by_id("u1")
        assert found is not None
        assert found.id == "u1"
        assert found.email == "alice@example.com"

    async def test_find_by_id_returns_none_when_not_found(self, repo):
        """find_by_id() should return None for a nonexistent id."""
        assert await repo.find_by_id("nonexistent") is None
