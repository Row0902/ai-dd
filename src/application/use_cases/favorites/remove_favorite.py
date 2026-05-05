"""Remove favorite use case (idempotent)."""

from __future__ import annotations

from domain.favorites.repositories import FavoriteRepository


async def remove_favorite(
    repo: FavoriteRepository,
    *,
    user_id: str,
    book_id: str,
) -> None:
    """Remove a book from the user's favorites.

    Idempotent: removing a nonexistent favorite is a no-op.

    Args:
        repo: Repository port.
        user_id: The user's ID.
        book_id: The book's ID.
    """
    await repo.remove(user_id, book_id)
