"""List collections use case."""

from __future__ import annotations

import builtins

from domain.auth.entities import UserRole
from domain.collections.entities import Collection
from domain.collections.repositories import CollectionRepository


async def list_collections(
    repo: CollectionRepository,
    *,
    user_id: str,
    role: UserRole,
) -> builtins.list[Collection]:
    """List collections visible to the user.

    Admin sees all collections; standard user sees only their own.

    Args:
        repo: Repository port.
        user_id: The requesting user's ID.
        role: The requesting user's role.

    Returns:
        List of collections visible to the user.
    """
    if role == UserRole.ADMIN:
        return await repo.list_all()
    return await repo.find_by_owner_id(user_id)
