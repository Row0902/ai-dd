"""In-memory invitation repository for testing and development."""

from __future__ import annotations

from domain.auth.entities import Invitation
from domain.auth.ports import InvitationRepository


class InMemoryInvitationRepository(InvitationRepository):
    """Dict-backed invitation repository.

    Intended for testing and development. Replaced by SQLInvitationRepository
    when session management is wired.
    """

    def __init__(self) -> None:
        """Initialize with an empty store."""
        self._invitations: dict[str, Invitation] = {}
        self._by_token: dict[str, str] = {}

    async def save(self, invitation: Invitation) -> Invitation:
        """Persist an invitation and return the saved entity.

        Args:
            invitation: Invitation entity to save.

        Returns:
            The saved invitation.
        """
        self._invitations[invitation.id] = invitation
        self._by_token[invitation.token] = invitation.id
        return invitation

    async def find_by_token(self, token: str) -> Invitation | None:
        """Find an invitation by its UUID4 token, or None.

        Args:
            token: Invitation token to search for.

        Returns:
            Invitation if found, None otherwise.
        """
        inv_id = self._by_token.get(token)
        if inv_id is None:
            return None
        return self._invitations.get(inv_id)

    async def mark_as_used(self, token: str) -> bool:
        """Mark an invitation as consumed.

        Args:
            token: Invitation token to mark as used.

        Returns:
            True if found and updated, False otherwise.
        """
        inv_id = self._by_token.get(token)
        if inv_id is None:
            return False
        invitation = self._invitations.get(inv_id)
        if invitation is None:
            return False
        from datetime import UTC, datetime

        invitation.used_at = datetime.now(UTC)
        return True
