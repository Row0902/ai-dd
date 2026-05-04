"""Unit tests for add_favorite use case."""

from __future__ import annotations

import builtins
from datetime import UTC, datetime

from application.use_cases.favorites.add_favorite import add_favorite
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


class TestAddFavorite:
    """Tests for add_favorite use case."""

    async def test_add_favorite_calls_repo(self) -> None:
        """add_favorite delegates to repository."""
        repo = InMemoryFavoriteRepository()
        await add_favorite(repo, user_id="u1", book_id="b1")
        assert await repo.list_by_user("u1") == ["b1"]

    async def test_add_favorite_is_idempotent(self) -> None:
        """Adding the same favorite twice does not error."""
        repo = InMemoryFavoriteRepository()
        await add_favorite(repo, user_id="u1", book_id="b1")
        await add_favorite(repo, user_id="u1", book_id="b1")
        assert await repo.list_by_user("u1") == ["b1"]

    async def test_add_favorite_multiple_books(self) -> None:
        """Adding different books creates multiple favorites."""
        repo = InMemoryFavoriteRepository()
        await add_favorite(repo, user_id="u1", book_id="b1")
        await add_favorite(repo, user_id="u1", book_id="b2")
        result = await repo.list_by_user("u1")
        assert len(result) == 2
        assert set(result) == {"b1", "b2"}
