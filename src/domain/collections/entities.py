"""Collection domain entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Collection:
    """Collection entity grouping books under a named set.

    Attributes:
        id: Unique identifier (UUID hex).
        name: Collection name.
        description: Optional description.
        owner_id: User ID of the owner.
        book_ids: Ordered list of book IDs in this collection.
        created_at: Timestamp of creation.
        updated_at: Timestamp of last update.
    """

    id: str
    name: str
    description: str = ""
    owner_id: str = ""
    book_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
