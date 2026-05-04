"""Unit tests for create_collection use case."""

from __future__ import annotations

import builtins

from application.use_cases.collections.create_collection import create_collection
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


class TestCreateCollection:
    """Tests for create_collection use case."""

    async def test_create_collection_returns_entity_with_id(self) -> None:
        """Create returns a Collection with a generated id."""
        repo = InMemoryCollectionRepository()
        result = await create_collection(
            repo, name="My Books", description="desc", owner_id="user-1"
        )
        assert result.id
        assert result.name == "My Books"
        assert result.description == "desc"
        assert result.owner_id == "user-1"
        assert result.book_ids == []

    async def test_create_collection_persists_in_repo(self) -> None:
        """Create persists the collection in the repository."""
        repo = InMemoryCollectionRepository()
        result = await create_collection(repo, name="Test", owner_id="user-1")
        found = await repo.find_by_id(result.id)
        assert found == result

    async def test_create_collection_with_empty_description(self) -> None:
        """Create defaults to empty description when not provided."""
        repo = InMemoryCollectionRepository()
        result = await create_collection(repo, name="Test", owner_id="user-1")
        assert result.description == ""
