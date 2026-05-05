"""Create invitation use case.

Handles invitation creation with 7-day expiry and notification dispatch.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from domain.auth.entities import Invitation, UserRole
from domain.auth.ports import InvitationRepository, NotificationService


async def create_invitation(
    repo: InvitationRepository,
    notification: NotificationService,
    inviter_id: str,
    inviter_name: str,
    email: str,
    role: UserRole,
) -> Invitation:
    """Create a new invitation and send a notification.

    Args:
        repo: Invitation repository port.
        notification: Notification service port.
        inviter_id: User ID of the admin creating the invitation.
        inviter_name: Name of the admin (for the notification).
        email: Invitee email address.
        role: Role the invitee will receive.

    Returns:
        The persisted Invitation entity.
    """
    invitation = Invitation(
        id=uuid.uuid4().hex,
        token=uuid.uuid4().hex,
        email=email,
        role=role,
        inviter_id=inviter_id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    saved = await repo.save(invitation)
    await notification.send_invitation(email, invitation.token, inviter_name)
    return saved
