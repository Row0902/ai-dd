"""SQL-backed collection repository implementation.

Implements the ``CollectionRepository`` port using async SQLAlchemy sessions
and the Data Mapper pattern (``CollectionMapper``).
"""

from __future__ import annotations

import builtins
from typing import override

from sqlalchemy import column, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.collections.entities import Collection
from domain.collections.repositories import CollectionRepository
from infrastructure.persistence.collection_mapper import CollectionMapper
from infrastructure.persistence.collection_models import CollectionModel


class SQLCollectionRepository(CollectionRepository):
    """CollectionRepository backed by a SQL database via async SQLAlchemy.

    Args:
        session: An AsyncSession instance.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with an async database session.

        Args:
            session: Active async SQLAlchemy session for database operations.
        """
        self._session = session

    @override
    async def save(self, collection: Collection) -> Collection:
        """Save (create or update) a collection.

        Uses session.merge() for upsert behavior — creates if new,
        updates if existing.

        Args:
            collection: The collection entity to persist.

        Returns:
            The persisted collection.
        """
        model = CollectionMapper.to_model(collection)
        merged = await self._session.merge(model)
        await self._session.commit()
        await self._session.refresh(merged)
        return CollectionMapper.to_domain(merged)

    @override
    async def find_by_id(self, collection_id: str) -> Collection | None:
        """Find a collection by ID.

        Args:
            collection_id: Unique identifier.

        Returns:
            Collection if found, None otherwise.
        """
        model = await self._session.get(CollectionModel, collection_id)
        if model is None:
            return None
        return CollectionMapper.to_domain(model)

    @override
    async def find_by_owner_id(self, owner_id: str) -> builtins.list[Collection]:
        """Find all collections owned by a user.

        Args:
            owner_id: The owner's user ID.

        Returns:
            List of collections owned by the user.
        """
        statement = select(CollectionModel).where(column("owner_id") == owner_id)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [CollectionMapper.to_domain(m) for m in models]

    @override
    async def list_all(self) -> builtins.list[Collection]:
        """List all collections.

        Returns:
            List of all collections.
        """
        statement = select(CollectionModel)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [CollectionMapper.to_domain(m) for m in models]

    @override
    async def delete(self, collection_id: str) -> bool:
        """Delete a collection by ID.

        Args:
            collection_id: Unique identifier.

        Returns:
            True if deleted, False if not found.
        """
        model = await self._session.get(CollectionModel, collection_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True
