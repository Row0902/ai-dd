"""SQL-backed invitation repository implementation.

Implements the ``InvitationRepository`` port using async SQLAlchemy sessions.
Domain ``Invitation`` entities are converted to/from ``InvitationModel``
inline.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.auth.entities import Invitation, UserRole
from domain.auth.ports import InvitationRepository
from infrastructure.auth.sql_models import InvitationModel


class SQLInvitationRepository(InvitationRepository):
    """InvitationRepository backed by a SQL database via async SQLAlchemy.

    The session is injected via constructor for testability and
    per-request scoping.

    Args:
        session: An AsyncSession instance.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with an async database session.

        Args:
            session: Active async SQLAlchemy session for database operations.
        """
        self._session = session

    @override
    async def save(self, invitation: Invitation) -> Invitation:
        """Persist an invitation and return the saved entity.

        Args:
            invitation: Domain Invitation entity to persist.

        Returns:
            The persisted Invitation entity.
        """
        model = InvitationModel(
            id=invitation.id,
            token=invitation.token,
            email=invitation.email,
            role=invitation.role.value,
            inviter_id=invitation.inviter_id,
            created_at=invitation.created_at,
            expires_at=invitation.expires_at,  # ty: ignore[invalid-argument-type]
            used_at=invitation.used_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_domain(model)

    @override
    async def find_by_token(self, token: str) -> Invitation | None:
        """Find an invitation by its UUID4 token.

        Args:
            token: The invitation token to search for.

        Returns:
            Invitation if found, None otherwise.
        """
        stmt = select(InvitationModel).where(InvitationModel.token == token)  # ty: ignore[invalid-argument-type]
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return _to_domain(model)

    @override
    async def mark_as_used(self, token: str) -> bool:
        """Mark an invitation as consumed.

        Args:
            token: The invitation token to mark as used.

        Returns:
            True if found and updated, False if not found.
        """
        stmt = select(InvitationModel).where(InvitationModel.token == token)  # ty: ignore[invalid-argument-type]
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return False
        model.used_at = datetime.now(UTC)
        self._session.add(model)
        await self._session.commit()
        return True


def _to_domain(model: InvitationModel) -> Invitation:
    """Convert an InvitationModel to a domain Invitation entity.

    Args:
        model: The SQLModel database row.

    Returns:
        Domain Invitation entity.
    """
    return Invitation(
        id=model.id,
        token=model.token,
        email=model.email,
        role=UserRole(model.role),
        inviter_id=model.inviter_id,
        created_at=model.created_at,
        expires_at=model.expires_at,
        used_at=model.used_at,
    )
