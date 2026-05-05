"""Tests for infrastructure.auth.logging_notification_service.

Unit tests using caplog to verify logging behavior.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
async def service():
    """Provide a LoggingNotificationService instance."""
    from infrastructure.auth.logging_notification_service import (
        LoggingNotificationService,
    )

    return LoggingNotificationService()


class TestLoggingNotificationService:
    """Tests for send_invitation() logging behavior."""

    async def test_send_invitation_logs_email_and_truncated_token(
        self, service, caplog
    ):
        """send_invitation() should log the email and a truncated token."""
        import logging

        with caplog.at_level(logging.DEBUG):
            await service.send_invitation(
                email="bob@example.com",
                token="abcdefgh1234567890",
                inviter_name="Alice",
            )
        assert "bob@example.com" in caplog.text
        assert "abcdefgh..." in caplog.text

    async def test_send_invitation_does_not_log_full_token(self, service, caplog):
        """send_invitation() should NOT log the full token (security)."""
        import logging

        full_token = "abcdefgh1234567890"
        with caplog.at_level(logging.DEBUG):
            await service.send_invitation(
                email="bob@example.com",
                token=full_token,
                inviter_name="Alice",
            )
        # The full token should NOT appear — only the truncated form
        assert full_token not in caplog.text

    async def test_send_invitation_logs_inviter_name(self, service, caplog):
        """send_invitation() should log the inviter name."""
        import logging

        with caplog.at_level(logging.DEBUG):
            await service.send_invitation(
                email="bob@example.com",
                token="abcdefgh1234567890",
                inviter_name="Alice",
            )
        assert "Alice" in caplog.text
