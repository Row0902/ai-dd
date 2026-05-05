"""In-memory collection repository for development and testing."""

from __future__ import annotations

import builtins

from domain.collections.entities import Collection
from domain.collections.repositories import CollectionRepository


class InMemoryCollectionRepository(CollectionRepository):
    """Dict-backed collection repository (thread-safe for single-process use)."""

    def __init__(self) -> None:
        """Initialize empty in-memory store."""
        self._collections: dict[str, Collection] = {}

    async def save(self, collection: Collection) -> Collection:
        """Save (create or update) a collection.

        Args:
            collection: The collection entity to persist.

        Returns:
            The persisted collection.
        """
        self._collections[collection.id] = collection
        return collection

    async def find_by_id(self, collection_id: str) -> Collection | None:
        """Find a collection by ID.

        Args:
            collection_id: Unique identifier.

        Returns:
            Collection if found, None otherwise.
        """
        return self._collections.get(collection_id)

    async def find_by_owner_id(self, owner_id: str) -> builtins.list[Collection]:
        """Find all collections owned by a user.

        Args:
            owner_id: The owner's user ID.

        Returns:
            List of collections owned by the user.
        """
        return [c for c in self._collections.values() if c.owner_id == owner_id]

    async def list_all(self) -> builtins.list[Collection]:
        """List all collections.

        Returns:
            List of all collections.
        """
        return list(self._collections.values())

    async def delete(self, collection_id: str) -> bool:
        """Delete a collection by ID.

        Args:
            collection_id: Unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        return self._collections.pop(collection_id, None) is not None
