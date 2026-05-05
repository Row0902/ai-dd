"""SQLModel table definitions for favorite persistence.

``FavoriteModel`` is a junction table linking users to books.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class FavoriteModel(SQLModel, table=True):  # type: ignore[call-arg]
    """SQLModel junction table for user-book favorites.

    Attributes:
        user_id: The user's ID (composite PK).
        book_id: The book's ID (composite PK).
        added_at: Timestamp when the favorite was added.
    """

    __tablename__ = "favorites"

    user_id: str = Field(primary_key=True)
    book_id: str = Field(primary_key=True)
    added_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
