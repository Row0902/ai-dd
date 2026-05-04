"""Delete collection use case with ownership enforcement."""

from __future__ import annotations

from domain.auth.entities import UserRole
from domain.auth.exceptions import AuthorizationError
from domain.collections.repositories import CollectionRepository


async def delete_collection(
    repo: CollectionRepository,
    collection_id: str,
    *,
    user_id: str,
    role: UserRole,
) -> bool:
    """Delete a collection with ownership check.

    Admin can delete any collection. Standard users can only delete their own.

    Args:
        repo: Repository port.
        collection_id: The collection to delete.
        user_id: The requesting user's ID.
        role: The requesting user's role.

    Returns:
        True if deleted, False if not found.

    Raises:
        AuthorizationError: If a non-admin user tries to delete another's collection.
    """
    collection = await repo.find_by_id(collection_id)
    if collection is None:
        return False
    if role != UserRole.ADMIN and collection.owner_id != user_id:
        raise AuthorizationError("Access denied")
    return await repo.delete(collection_id)
