"""Unit tests for delete_collection use case."""

from __future__ import annotations

import builtins

import pytest

from application.use_cases.collections.create_collection import create_collection
from application.use_cases.collections.delete_collection import delete_collection
from domain.auth.entities import UserRole
from domain.auth.exceptions import AuthorizationError
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


class TestDeleteCollection:
    """Tests for delete_collection use case with ownership checks."""

    async def test_owner_can_delete_own_collection(self) -> None:
        """User can delete their own collection."""
        repo = InMemoryCollectionRepository()
        col = await create_collection(repo, name="Mine", owner_id="user-1")
        result = await delete_collection(
            repo, col.id, user_id="user-1", role=UserRole.USER
        )
        assert result is True
        assert await repo.find_by_id(col.id) is None

    async def test_user_cannot_delete_other_users_collection(self) -> None:
        """User cannot delete another user's collection — raises AuthorizationError."""
        repo = InMemoryCollectionRepository()
        col = await create_collection(repo, name="Theirs", owner_id="user-2")
        with pytest.raises(AuthorizationError):
            await delete_collection(
                repo, col.id, user_id="user-1", role=UserRole.USER
            )
        # Collection must still exist
        assert await repo.find_by_id(col.id) is not None

    async def test_admin_can_delete_any_collection(self) -> None:
        """Admin can delete any collection regardless of owner."""
        repo = InMemoryCollectionRepository()
        col = await create_collection(repo, name="Anyones", owner_id="user-1")
        result = await delete_collection(
            repo, col.id, user_id="admin-1", role=UserRole.ADMIN
        )
        assert result is True
        assert await repo.find_by_id(col.id) is None

    async def test_delete_nonexistent_returns_false(self) -> None:
        """Deleting a nonexistent collection returns False."""
        repo = InMemoryCollectionRepository()
        result = await delete_collection(
            repo, "missing", user_id="user-1", role=UserRole.USER
        )
        assert result is False
