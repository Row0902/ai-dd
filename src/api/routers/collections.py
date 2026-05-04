"""Collections router.

Endpoints for CRUD operations on collections with ownership enforcement.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from api.dependencies import get_collection_repo
from api.middleware.auth import require_permission
from application.use_cases.collections.create_collection import create_collection
from application.use_cases.collections.delete_collection import delete_collection
from application.use_cases.collections.list_collections import list_collections
from domain.auth.entities import UserRole
from domain.auth.permissions import Operation
from domain.collections.repositories import CollectionRepository

router = APIRouter(prefix="/collections", tags=["collections"])


class CollectionPayload(BaseModel):
    """Request payload for creating a collection."""

    name: str
    description: str = ""


def _collection_to_dict(c) -> dict:
    """Convert a Collection entity to HTTP JSON representation."""
    return {
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "owner_id": c.owner_id,
        "book_ids": c.book_ids,
        "created_at": c.created_at.isoformat(),
        "updated_at": c.updated_at.isoformat(),
    }


@router.post("", status_code=201)
async def create_collection_endpoint(
    payload: CollectionPayload,
    repo: Annotated[CollectionRepository, Depends(get_collection_repo)],
    user: dict = Depends(require_permission(Operation.COLLECTION_CREATE)),
):
    """Create a new collection owned by the authenticated user.

    Args:
        payload: Collection name and optional description.
        repo: Collection repository injected via dependency.
        user: Current user claims from auth middleware.
    """
    col = await create_collection(
        repo,
        name=payload.name,
        description=payload.description,
        owner_id=user["user_id"],
    )
    return _collection_to_dict(col)


@router.get("")
async def list_collections_endpoint(
    repo: Annotated[CollectionRepository, Depends(get_collection_repo)],
    user: dict = Depends(require_permission(Operation.COLLECTION_READ)),
):
    """List collections visible to the authenticated user.

    Admin sees all; standard user sees only their own.

    Args:
        repo: Collection repository injected via dependency.
        user: Current user claims from auth middleware.
    """
    role = user["role"]
    if isinstance(role, str):
        role = UserRole(role)
    cols = await list_collections(
        repo, user_id=user["user_id"], role=role
    )
    return [_collection_to_dict(c) for c in cols]


@router.delete("/{collection_id}", status_code=204)
async def delete_collection_endpoint(
    collection_id: str,
    repo: Annotated[CollectionRepository, Depends(get_collection_repo)],
    user: dict = Depends(require_permission(Operation.COLLECTION_DELETE)),
):
    """Delete a collection. Owner or admin only.

    Args:
        collection_id: The collection to delete.
        repo: Collection repository injected via dependency.
        user: Current user claims from auth middleware.
    """
    role = user["role"]
    if isinstance(role, str):
        role = UserRole(role)
    deleted = await delete_collection(
        repo, collection_id, user_id=user["user_id"], role=role
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(status_code=204)
