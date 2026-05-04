"""Create collection use case."""

from __future__ import annotations

import uuid

from domain.collections.entities import Collection
from domain.collections.repositories import CollectionRepository


async def create_collection(
    repo: CollectionRepository,
    *,
    name: str,
    description: str = "",
    owner_id: str,
) -> Collection:
    """Create a new collection.

    Args:
        repo: Repository port.
        name: Collection name.
        description: Optional description.
        owner_id: User ID of the owner.

    Returns:
        The persisted collection entity.
    """
    collection = Collection(
        id=uuid.uuid4().hex,
        name=name,
        description=description,
        owner_id=owner_id,
    )
    return await repo.save(collection)
