"""List favorites use case."""

from __future__ import annotations

import builtins

from domain.favorites.repositories import FavoriteRepository


async def list_favorites(
    repo: FavoriteRepository,
    *,
    user_id: str,
) -> builtins.list[str]:
    """List the user's favorite book IDs in reverse chronological order.

    Args:
        repo: Repository port.
        user_id: The user's ID.

    Returns:
        Ordered list of book IDs (most recently added first).
    """
    return await repo.list_by_user(user_id)
