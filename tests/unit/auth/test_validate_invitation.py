"""Tests for application.use_cases.auth.validate_invitation.

Unit tests with mocked dependencies.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from domain.auth.entities import Invitation, UserRole
from domain.auth.exceptions import InvitationError


@pytest.fixture()
def mock_repo():
    """Provide a mock InvitationRepository."""
    repo = AsyncMock()
    return repo


def _make_invitation(
    *,
    used_at: datetime | None = None,
    expires_at: datetime | None = None,
) -> Invitation:
    """Create a test Invitation with sensible defaults."""
    return Invitation(
        id="inv1",
        token="tok-abc",
        email="bob@example.com",
        role=UserRole.USER,
        inviter_id="admin1",
        expires_at=expires_at or (datetime.now(UTC) + timedelta(days=7)),
        used_at=used_at,
    )


class TestValidateInvitation:
    """Tests for validate_invitation use case."""

    async def test_validate_invitation_returns_invitation_on_valid(self, mock_repo):
        """validate_invitation() should return the invitation when valid."""
        from application.use_cases.auth.validate_invitation import validate_invitation

        mock_repo.find_by_token.return_value = _make_invitation()

        result = await validate_invitation(repo=mock_repo, token="tok-abc")
        assert result.email == "bob@example.com"
        assert result.token == "tok-abc"

    async def test_validate_invitation_raises_when_not_found(self, mock_repo):
        """validate_invitation() should raise InvitationError when not found."""
        from application.use_cases.auth.validate_invitation import validate_invitation

        mock_repo.find_by_token.return_value = None

        with pytest.raises(InvitationError):
            await validate_invitation(repo=mock_repo, token="nonexistent")

    async def test_validate_invitation_raises_when_expired(self, mock_repo):
        """validate_invitation() should raise InvitationError when expired."""
        from application.use_cases.auth.validate_invitation import validate_invitation

        mock_repo.find_by_token.return_value = _make_invitation(
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )

        with pytest.raises(InvitationError):
            await validate_invitation(repo=mock_repo, token="tok-abc")

    async def test_validate_invitation_raises_when_already_used(self, mock_repo):
        """validate_invitation() should raise InvitationError when already used."""
        from application.use_cases.auth.validate_invitation import validate_invitation

        mock_repo.find_by_token.return_value = _make_invitation(
            used_at=datetime.now(UTC),
        )

        with pytest.raises(InvitationError):
            await validate_invitation(repo=mock_repo, token="tok-abc")
