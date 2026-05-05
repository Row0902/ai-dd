"""Validate invitation use case.

Handles invitation token validation: existence, expiry, and usage checks.
"""

from __future__ import annotations

from datetime import UTC, datetime

from domain.auth.entities import Invitation
from domain.auth.exceptions import InvitationError
from domain.auth.ports import InvitationRepository


async def validate_invitation(
    repo: InvitationRepository,
    token: str,
) -> Invitation:
    """Validate an invitation token.

    Args:
        repo: Invitation repository port.
        token: The invitation token to validate.

    Returns:
        The validated Invitation entity.

    Raises:
        InvitationError: If the token is not found, expired, or already used.
    """
    invitation = await repo.find_by_token(token)
    if invitation is None:
        raise InvitationError("Invitation not found")
    if invitation.used_at is not None:
        raise InvitationError("Invitation already used")
    if invitation.expires_at and invitation.expires_at < datetime.now(UTC):
        raise InvitationError("Invitation expired")
    return invitation
