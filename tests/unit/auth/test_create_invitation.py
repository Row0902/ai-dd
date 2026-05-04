"""Tests for application.use_cases.auth.create_invitation.

Unit tests with mocked dependencies.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from domain.auth.entities import Invitation, UserRole


@pytest.fixture()
def mock_repo():
    """Provide a mock InvitationRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture()
def mock_notification():
    """Provide a mock NotificationService."""
    return AsyncMock()


class TestCreateInvitation:
    """Tests for create_invitation use case."""

    async def test_create_invitation_saves_and_notifies(
        self, mock_repo, mock_notification
    ):
        """create_invitation() should save the invitation and send notification."""
        from application.use_cases.auth.create_invitation import create_invitation

        mock_repo.save.return_value = Invitation(
            id="inv1",
            token="tok-abc",
            email="bob@example.com",
            role=UserRole.USER,
            inviter_id="admin1",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )

        result = await create_invitation(
            repo=mock_repo,
            notification=mock_notification,
            inviter_id="admin1",
            inviter_name="Alice",
            email="bob@example.com",
            role=UserRole.USER,
        )
        assert result.email == "bob@example.com"
        mock_repo.save.assert_called_once()
        mock_notification.send_invitation.assert_called_once()

    async def test_create_invitation_sets_7_day_expiry(
        self, mock_repo, mock_notification
    ):
        """create_invitation() should set expires_at to 7 days from now."""
        from application.use_cases.auth.create_invitation import create_invitation

        mock_repo.save.return_value = Invitation(
            id="inv1",
            token="tok-abc",
            email="bob@example.com",
            role=UserRole.USER,
            inviter_id="admin1",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )

        await create_invitation(
            repo=mock_repo,
            notification=mock_notification,
            inviter_id="admin1",
            inviter_name="Alice",
            email="bob@example.com",
            role=UserRole.USER,
        )
        saved_inv = mock_repo.save.call_args[0][0]
        expected_expiry = datetime.now(UTC) + timedelta(days=7)
        # Allow 5 seconds tolerance for test execution time
        assert abs((saved_inv.expires_at - expected_expiry).total_seconds()) < 5

    async def test_create_invitation_passes_token_to_notification(
        self, mock_repo, mock_notification
    ):
        """create_invitation() should pass a UUID hex token to the notification."""
        from application.use_cases.auth.create_invitation import create_invitation

        mock_repo.save.return_value = Invitation(
            id="inv1",
            token="tok-abc",
            email="bob@example.com",
            role=UserRole.USER,
            inviter_id="admin1",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )

        await create_invitation(
            repo=mock_repo,
            notification=mock_notification,
            inviter_id="admin1",
            inviter_name="Alice",
            email="bob@example.com",
            role=UserRole.USER,
        )
        call_args = mock_notification.send_invitation.call_args
        token = call_args[0][1]
        assert call_args[0][0] == "bob@example.com"  # email
        assert len(token) == 32  # UUID4 hex is 32 chars
        assert call_args[0][2] == "Alice"  # inviter_name
