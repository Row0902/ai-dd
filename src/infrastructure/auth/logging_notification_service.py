"""Logging-based notification service implementing the NotificationService port.

Sends invitation notifications via structured logging (for development /
testing).  A production adapter would integrate with an email provider.
"""

from __future__ import annotations

import logging
from typing import override

from domain.auth.ports import NotificationService

logger = logging.getLogger(__name__)


class LoggingNotificationService(NotificationService):
    """NotificationService that logs invitation details.

    The token is truncated in the log output for security — only the
    first 8 characters are emitted.
    """

    @override
    async def send_invitation(self, email: str, token: str, inviter_name: str) -> None:
        """Log an invitation notification.

        Args:
            email: Invitee email address.
            token: The invitation token (truncated in log output).
            inviter_name: Name of the admin who created the invitation.
        """
        truncated = f"{token[:8]}..."
        logger.info(
            "[INVITATION] To: %s, Token: %s, Inviter: %s",
            email,
            truncated,
            inviter_name,
        )
