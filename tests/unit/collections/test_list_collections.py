"""Unit tests for list_collections use case."""

from __future__ import annotations

import builtins

from application.use_cases.collections.create_collection import create_collection
from application.use_cases.collections.list_collections import list_collections
from domain.auth.entities import UserRole
from domain.collections.entities import Collection
from domain.collections.repositories import CollectionRepository


class InMemoryCollectionRepository(CollectionRepository):
    """Simple in-memory repository for unit tests."""

    def __init__(self) -> None:
        """Initialize empty in-memory store."""
        self._collections: dict[str, Collection] = {}

    async def save(self, collection: Collection) -> Collection:
        """Persist a collection."""
        self._collections[collection.id] = collection
        return collection

    async def find_by_id(self, collection_id: str) -> Collection | None:
        """Find by id."""
        return self._collections.get(collection_id)

    async def find_by_owner_id(self, owner_id: str) -> builtins.list[Collection]:
        """Find by owner."""
        return [c for c in self._collections.values() if c.owner_id == owner_id]

    async def list_all(self) -> builtins.list[Collection]:
        """List all."""
        return list(self._collections.values())

    async def delete(self, collection_id: str) -> bool:
        """Delete by id."""
        return self._collections.pop(collection_id, None) is not None


class TestListCollections:
    """Tests for list_collections use case."""

    async def test_user_sees_only_own_collections(self) -> None:
        """Standard user only sees collections they own."""
        repo = InMemoryCollectionRepository()
        await create_collection(repo, name="User1 Col", owner_id="user-1")
        await create_collection(repo, name="User2 Col", owner_id="user-2")

        result = await list_collections(repo, user_id="user-1", role=UserRole.USER)
        assert len(result) == 1
        assert result[0].name == "User1 Col"

    async def test_admin_sees_all_collections(self) -> None:
        """Admin sees collections from all users."""
        repo = InMemoryCollectionRepository()
        await create_collection(repo, name="User1 Col", owner_id="user-1")
        await create_collection(repo, name="User2 Col", owner_id="user-2")

        result = await list_collections(repo, user_id="admin-1", role=UserRole.ADMIN)
        assert len(result) == 2

    async def test_list_collections_empty(self) -> None:
        """Listing on empty repo returns empty list."""
        repo = InMemoryCollectionRepository()
        result = await list_collections(repo, user_id="user-1", role=UserRole.USER)
        assert result == []
