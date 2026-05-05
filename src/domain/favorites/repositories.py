"""Favorite repository port: abstract interface for persistence adapters."""

from __future__ import annotations

import builtins
from abc import ABC, abstractmethod


class FavoriteRepository(ABC):
    """Port for favorite persistence.

    Per ADR-7: no Favorite entity — just junction table operations.
    """

    @abstractmethod
    async def add(self, user_id: str, book_id: str) -> None:
        """Add a book to a user's favorites (idempotent).

        Args:
            user_id: The user's ID.
            book_id: The book's ID.
        """

    @abstractmethod
    async def remove(self, user_id: str, book_id: str) -> None:
        """Remove a book from a user's favorites (idempotent).

        Args:
            user_id: The user's ID.
            book_id: The book's ID.
        """

    @abstractmethod
    async def list_by_user(self, user_id: str) -> builtins.list[str]:
        """List favorite book IDs for a user, reverse chronological.

        Args:
            user_id: The user's ID.

        Returns:
            Ordered list of book IDs (most recently added first).
        """
