"""SQLModel table definitions for book persistence.

``BookModel`` is a plain SQLModel data class — NOT a domain entity.
It mirrors the flat column structure of the ``books`` table and is
mapped to/from the domain ``Book`` entity via ``BookMapper``.
"""

from __future__ import annotations

from sqlmodel import Field, SQLModel


class BookModel(SQLModel, table=True):  # type: ignore[call-arg]
    """SQLModel table for books.

    Attributes:
        id: Primary key (UUID hex string).
        name: Book title.
        author: Author name (empty string if unset).
        description: Extended description.
        url: Reference URL (empty string if unset).
        content: Book content or summary.
    """

    __tablename__ = "books"

    id: str = Field(primary_key=True)
    name: str
    author: str = ""
    description: str = ""
    url: str = ""
    content: str = ""
