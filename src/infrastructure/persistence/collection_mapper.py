"""Bidirectional mapping between CollectionModel and domain Collection entity.

Implements the Data Mapper pattern: ``CollectionModel`` (SQLModel table) is
translated to/from ``Collection`` (domain entity) with JSON deserialization
for the ``book_ids`` field.
"""

from __future__ import annotations

import json

from domain.collections.entities import Collection
from infrastructure.persistence.collection_models import CollectionModel


class CollectionMapper:
    """Stateless mapper between CollectionModel and Collection.

    All methods are static — no instance state needed.
    """

    @staticmethod
    def to_domain(model: CollectionModel) -> Collection:
        """Translate a CollectionModel to a domain Collection entity.

        Args:
            model: The SQLModel database row.

        Returns:
            A fully-constructed domain Collection entity.
        """
        book_ids = json.loads(model.book_ids) if model.book_ids else []
        return Collection(
            id=model.id,
            name=model.name,
            description=model.description,
            owner_id=model.owner_id,
            book_ids=book_ids,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Collection) -> CollectionModel:
        """Translate a domain Collection entity to a CollectionModel.

        Args:
            entity: The domain Collection entity.

        Returns:
            A CollectionModel instance ready for database persistence.
        """
        return CollectionModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            owner_id=entity.owner_id,
            book_ids=json.dumps(entity.book_ids),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
