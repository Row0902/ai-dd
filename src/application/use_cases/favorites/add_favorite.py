"""Add favorite use case (idempotent)."""

from __future__ import annotations

from domain.favorites.repositories import FavoriteRepository


async def add_favorite(
    repo: FavoriteRepository,
    *,
    user_id: str,
    book_id: str,
) -> None:
    """Add a book to the user's favorites.

    Idempotent: adding the same favorite twice is a no-op.

    Args:
        repo: Repository port.
        user_id: The user's ID.
        book_id: The book's ID.
    """
    await repo.add(user_id, book_id)
