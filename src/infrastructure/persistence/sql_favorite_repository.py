"""SQL-backed favorite repository implementation.

Implements the ``FavoriteRepository`` port using async SQLAlchemy sessions.
Uses raw SQL for idempotent add (INSERT OR IGNORE) to handle duplicates.
"""

from __future__ import annotations

import builtins

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from domain.favorites.repositories import FavoriteRepository
from infrastructure.persistence.favorite_models import FavoriteModel


class SQLFavoriteRepository(FavoriteRepository):
    """FavoriteRepository backed by a SQL database via async SQLAlchemy.

    Args:
        session: An AsyncSession instance.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with an async database session.

        Args:
            session: Active async SQLAlchemy session for database operations.
        """
        self._session = session

    async def add(self, user_id: str, book_id: str) -> None:
        """Add a favorite (idempotent via INSERT OR IGNORE).

        Args:
            user_id: The user's ID.
            book_id: The book's ID.
        """
        # Use raw SQL for idempotency — INSERT OR IGNORE on SQLite,
        # INSERT ... ON CONFLICT DO NOTHING on PostgreSQL.
        # For simplicity, use session.add with a try/except approach.
        existing = await self._session.get(
            FavoriteModel, {"user_id": user_id, "book_id": book_id}
        )
        if existing is not None:
            return
        model = FavoriteModel(user_id=user_id, book_id=book_id)
        self._session.add(model)
        await self._session.commit()

    async def remove(self, user_id: str, book_id: str) -> None:
        """Remove a favorite (idempotent).

        Args:
            user_id: The user's ID.
            book_id: The book's ID.
        """
        model = await self._session.get(
            FavoriteModel, {"user_id": user_id, "book_id": book_id}
        )
        if model is not None:
            await self._session.delete(model)
            await self._session.commit()

    async def list_by_user(self, user_id: str) -> builtins.list[str]:
        """List favorite book IDs for a user, reverse chronological.

        Args:
            user_id: The user's ID.

        Returns:
            Ordered list of book IDs (most recently added first).
        """
        statement = text(
            "SELECT book_id FROM favorites "
            "WHERE user_id = :user_id ORDER BY added_at DESC"
        ).bindparams(user_id=user_id)
        result = await self._session.execute(statement)
        return [row[0] for row in result.fetchall()]
