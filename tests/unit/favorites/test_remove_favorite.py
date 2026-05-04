"""Unit tests for remove_favorite use case."""

from __future__ import annotations

import builtins
from datetime import UTC, datetime

from application.use_cases.favorites.add_favorite import add_favorite
from application.use_cases.favorites.remove_favorite import remove_favorite
from domain.favorites.repositories import FavoriteRepository


class InMemoryFavoriteRepository(FavoriteRepository):
    """Simple in-memory repository for unit tests."""

    def __init__(self) -> None:
        """Initialize empty in-memory store."""
        self._favorites: dict[tuple[str, str], datetime] = {}

    async def add(self, user_id: str, book_id: str) -> None:
        """Add a favorite (idempotent)."""
        self._favorites[(user_id, book_id)] = datetime.now(UTC)

    async def remove(self, user_id: str, book_id: str) -> None:
        """Remove a favorite (idempotent)."""
        self._favorites.pop((user_id, book_id), None)

    async def list_by_user(self, user_id: str) -> builtins.list[str]:
        """List book_ids for a user, reverse chronological."""
        pairs = [
            (book_id, added_at)
            for (uid, book_id), added_at in self._favorites.items()
            if uid == user_id
        ]
        pairs.sort(key=lambda x: x[1], reverse=True)
        return [book_id for book_id, _ in pairs]


class TestRemoveFavorite:
    """Tests for remove_favorite use case."""

    async def test_remove_favorite_removes_from_repo(self) -> None:
        """remove_favorite removes the favorite from repository."""
        repo = InMemoryFavoriteRepository()
        await add_favorite(repo, user_id="u1", book_id="b1")
        await remove_favorite(repo, user_id="u1", book_id="b1")
        assert await repo.list_by_user("u1") == []

    async def test_remove_favorite_is_idempotent(self) -> None:
        """Removing a nonexistent favorite does not error."""
        repo = InMemoryFavoriteRepository()
        await remove_favorite(repo, user_id="u1", book_id="b1")
        assert await repo.list_by_user("u1") == []

    async def test_remove_favorite_leaves_others_intact(self) -> None:
        """Removing one favorite does not affect others."""
        repo = InMemoryFavoriteRepository()
        await add_favorite(repo, user_id="u1", book_id="b1")
        await add_favorite(repo, user_id="u1", book_id="b2")
        await remove_favorite(repo, user_id="u1", book_id="b1")
        assert await repo.list_by_user("u1") == ["b2"]
