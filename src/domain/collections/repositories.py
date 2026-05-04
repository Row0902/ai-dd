"""Collection repository port: abstract interface for persistence adapters."""

from __future__ import annotations

import builtins
from abc import ABC, abstractmethod

from domain.collections.entities import Collection


class CollectionRepository(ABC):
    """Port for collection persistence.

    Abstract interface defining the contract that any concrete repository
    must implement.
    """

    @abstractmethod
    async def save(self, collection: Collection) -> Collection:
        """Save (create or update) a collection.

        Args:
            collection: The collection entity to persist.

        Returns:
            The persisted collection.
        """

    @abstractmethod
    async def find_by_id(self, collection_id: str) -> Collection | None:
        """Find a collection by its ID.

        Args:
            collection_id: Unique identifier.

        Returns:
            Collection if found, None otherwise.
        """

    @abstractmethod
    async def find_by_owner_id(self, owner_id: str) -> builtins.list[Collection]:
        """Find all collections owned by a user.

        Args:
            owner_id: The owner's user ID.

        Returns:
            List of collections owned by the user.
        """

    @abstractmethod
    async def list_all(self) -> builtins.list[Collection]:
        """List all collections (admin use).

        Returns:
            List of all collections.
        """

    @abstractmethod
    async def delete(self, collection_id: str) -> bool:
        """Delete a collection by ID.

        Args:
            collection_id: Unique identifier.

        Returns:
            True if deleted, False if not found.
        """
