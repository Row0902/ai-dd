"""SQLModel table definitions for collection persistence.

``CollectionModel`` is a plain SQLModel data class — NOT a domain entity.
Book IDs are stored as a JSON string for simplicity (no junction table).
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class CollectionModel(SQLModel, table=True):  # type: ignore[call-arg]
    """SQLModel table for collections.

    Attributes:
        id: Primary key (UUID hex string).
        name: Collection name.
        description: Optional description.
        owner_id: User ID of the owner.
        book_ids: JSON-encoded list of book IDs.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "collections"

    id: str = Field(primary_key=True)
    name: str
    description: str = ""
    owner_id: str
    book_ids: str = "[]"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
