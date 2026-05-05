"""Favorites router.

Endpoints for managing user favorites (add, remove, list).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from api.dependencies import get_favorite_repo
from api.middleware.auth import require_permission
from application.use_cases.favorites.add_favorite import add_favorite
from application.use_cases.favorites.list_favorites import list_favorites
from application.use_cases.favorites.remove_favorite import remove_favorite
from domain.auth.permissions import Operation
from domain.favorites.repositories import FavoriteRepository

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post("/{book_id}", status_code=201)
async def add_favorite_endpoint(
    book_id: str,
    repo: Annotated[FavoriteRepository, Depends(get_favorite_repo)],
    user: dict = Depends(require_permission(Operation.FAVORITE_ADD)),
):
    """Add a book to the user's favorites (idempotent).

    Args:
        book_id: The book to favorite.
        repo: Favorite repository injected via dependency.
        user: Current user claims from auth middleware.
    """
    await add_favorite(repo, user_id=user["user_id"], book_id=book_id)
    return Response(status_code=201)


@router.delete("/{book_id}", status_code=204)
async def remove_favorite_endpoint(
    book_id: str,
    repo: Annotated[FavoriteRepository, Depends(get_favorite_repo)],
    user: dict = Depends(require_permission(Operation.FAVORITE_REMOVE)),
):
    """Remove a book from the user's favorites (idempotent).

    Args:
        book_id: The book to unfavorite.
        repo: Favorite repository injected via dependency.
        user: Current user claims from auth middleware.
    """
    await remove_favorite(repo, user_id=user["user_id"], book_id=book_id)
    return Response(status_code=204)


@router.get("")
async def list_favorites_endpoint(
    repo: Annotated[FavoriteRepository, Depends(get_favorite_repo)],
    user: dict = Depends(require_permission(Operation.COLLECTION_READ)),
):
    """List the user's favorite book IDs in reverse chronological order.

    Args:
        repo: Favorite repository injected via dependency.
        user: Current user claims from auth middleware.
    """
    return await list_favorites(repo, user_id=user["user_id"])
