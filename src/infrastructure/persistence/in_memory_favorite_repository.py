"""In-memory favorite repository for development and testing."""

from __future__ import annotations

import builtins
from datetime import UTC, datetime
from typing import override

from domain.favorites.repositories import FavoriteRepository


class InMemoryFavoriteRepository(FavoriteRepository):
    """Dict-backed favorite repository (thread-safe for single-process use)."""

    def __init__(self) -> None:
        """Initialize empty in-memory store."""
        self._favorites: dict[tuple[str, str], datetime] = {}

    @override
    async def add(self, user_id: str, book_id: str) -> None:
        """Add a favorite (idempotent).

        Args:
            user_id: The user's ID.
            book_id: The book's ID.
        """
        self._favorites[(user_id, book_id)] = datetime.now(UTC)

    @override
    async def remove(self, user_id: str, book_id: str) -> None:
        """Remove a favorite (idempotent).

        Args:
            user_id: The user's ID.
            book_id: The book's ID.
        """
        self._favorites.pop((user_id, book_id), None)

    @override
    async def list_by_user(self, user_id: str) -> builtins.list[str]:
        """List favorite book IDs for a user, reverse chronological.

        Args:
            user_id: The user's ID.

        Returns:
            Ordered list of book IDs (most recently added first).
        """
        pairs = [
            (book_id, added_at)
            for (uid, book_id), added_at in self._favorites.items()
            if uid == user_id
        ]
        pairs.sort(key=lambda x: x[1], reverse=True)
        return [book_id for book_id, _ in pairs]
