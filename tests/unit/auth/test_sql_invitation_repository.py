"""Tests for infrastructure.auth.sql_invitation_repository.

Integration tests using in-memory SQLite with async sessions.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from domain.auth.entities import Invitation, UserRole
from infrastructure.persistence.session import create_engine_from_url, create_tables


@pytest.fixture()
async def db_session():
    """Provide a fresh in-memory async SQLite session with auth tables created."""
    from infrastructure.persistence.session import get_session

    engine = create_engine_from_url("sqlite://")
    import infrastructure.auth.sql_models  # noqa: F401

    await create_tables(engine)
    async with get_session(engine) as session:
        yield session
    await engine.dispose()


@pytest.fixture()
async def repo(db_session):
    """Provide an SQLInvitationRepository bound to the test session."""
    from infrastructure.auth.sql_invitation_repository import SQLInvitationRepository

    return SQLInvitationRepository(db_session)


def _make_invitation(
    *,
    inv_id: str = "inv1",
    token: str = "tok-abc-123",
    email: str = "bob@example.com",
    role: UserRole = UserRole.USER,
    inviter_id: str = "admin1",
    expires_at: datetime | None = None,
    used_at: datetime | None = None,
) -> Invitation:
    """Create a test Invitation with sensible defaults."""
    return Invitation(
        id=inv_id,
        token=token,
        email=email,
        role=role,
        inviter_id=inviter_id,
        expires_at=expires_at or (datetime.now(UTC) + timedelta(days=7)),
        used_at=used_at,
    )


class TestSQLInvitationRepositorySave:
    """Tests for save() method."""

    async def test_save_persists_invitation(self, repo):
        """save() should persist a new invitation and return it."""
        inv = _make_invitation()
        saved = await repo.save(inv)
        assert saved.id == "inv1"
        assert saved.token == "tok-abc-123"
        assert saved.email == "bob@example.com"
        assert saved.role == UserRole.USER


class TestSQLInvitationRepositoryFindByToken:
    """Tests for find_by_token() method."""

    async def test_find_by_token_returns_invitation_when_found(self, repo):
        """find_by_token() should return the invitation when it exists."""
        inv = _make_invitation()
        await repo.save(inv)
        found = await repo.find_by_token("tok-abc-123")
        assert found is not None
        assert found.id == "inv1"
        assert found.email == "bob@example.com"

    async def test_find_by_token_returns_none_when_not_found(self, repo):
        """find_by_token() should return None for a nonexistent token."""
        assert await repo.find_by_token("nonexistent") is None


class TestSQLInvitationRepositoryMarkAsUsed:
    """Tests for mark_as_used() method."""

    async def test_mark_as_used_sets_used_at(self, repo):
        """mark_as_used() should set used_at and return True."""
        inv = _make_invitation()
        await repo.save(inv)
        result = await repo.mark_as_used("tok-abc-123")
        assert result is True
        found = await repo.find_by_token("tok-abc-123")
        assert found is not None
        assert found.used_at is not None

    async def test_mark_as_used_returns_false_when_not_found(self, repo):
        """mark_as_used() should return False for a nonexistent token."""
        assert await repo.mark_as_used("nonexistent") is False
