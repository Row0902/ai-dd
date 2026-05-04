"""Unit tests for list_favorites use case."""

from __future__ import annotations

import builtins
from datetime import UTC, datetime, timedelta

from application.use_cases.favorites.list_favorites import list_favorites
from domain.favorites.repositories import FavoriteRepository


class InMemoryFavoriteRepository(FavoriteRepository):
    """Simple in-memory repository for unit tests with controllable timestamps."""

    def __init__(self) -> None:
        """Initialize empty in-memory store."""
        self._favorites: dict[tuple[str, str], datetime] = {}

    async def add(self, user_id: str, book_id: str) -> None:
        """Add a favorite with current timestamp."""
        self._favorites[(user_id, book_id)] = datetime.now(UTC)

    async def add_with_ts(
        self, user_id: str, book_id: str, ts: datetime
    ) -> None:
        """Add with explicit timestamp for testing ordering."""
        self._favorites[(user_id, book_id)] = ts

    async def remove(self, user_id: str, book_id: str) -> None:
        """Remove a favorite."""
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


class TestListFavorites:
    """Tests for list_favorites use case."""

    async def test_list_favorites_empty(self) -> None:
        """Listing favorites with none added returns empty list."""
        repo = InMemoryFavoriteRepository()
        result = await list_favorites(repo, user_id="u1")
        assert result == []

    async def test_list_favorites_returns_book_ids(self) -> None:
        """Listing favorites returns the book IDs."""
        repo = InMemoryFavoriteRepository()
        await repo.add("u1", "b1")
        await repo.add("u1", "b2")
        result = await list_favorites(repo, user_id="u1")
        assert set(result) == {"b1", "b2"}

    async def test_list_favorites_reverse_chronological(self) -> None:
        """Favorites are returned in reverse chronological order."""
        repo = InMemoryFavoriteRepository()
        now = datetime.now(UTC)
        await repo.add_with_ts("u1", "b1", now - timedelta(hours=2))
        await repo.add_with_ts("u1", "b2", now - timedelta(hours=1))
        await repo.add_with_ts("u1", "b3", now)
        result = await list_favorites(repo, user_id="u1")
        assert result == ["b3", "b2", "b1"]

    async def test_list_favorites_only_own(self) -> None:
        """Users only see their own favorites."""
        repo = InMemoryFavoriteRepository()
        await repo.add("u1", "b1")
        await repo.add("u2", "b2")
        result = await list_favorites(repo, user_id="u1")
        assert result == ["b1"]
