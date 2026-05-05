"""Bidirectional mapping between BookModel and domain Book entity.

Implements the Data Mapper pattern: ``BookModel`` (SQLModel table) is
translated to/from ``Book`` (domain entity) with value-object
reconstruction on the domain side.
"""

from __future__ import annotations

from domain.entities import Book
from infrastructure.persistence.sql_models import BookModel


class BookMapper:
    """Stateless mapper between BookModel and Book.

    All methods are static — no instance state needed.
    """

    @staticmethod
    def to_domain(model: BookModel) -> Book:
        """Translate a BookModel to a domain Book entity.

        Reconstructs value objects (BookName, BookAuthor, BookUrl) from
        the flat string fields on the model.

        Args:
            model: The SQLModel database row.

        Returns:
            A fully-constructed domain Book entity.
        """
        return Book(
            id=model.id,
            name=model.name,
            author=model.author,
            url=model.url,
            description=model.description,
            content=model.content,
        )

    @staticmethod
    def to_model(entity: Book) -> BookModel:
        """Translate a domain Book entity to a BookModel.

        Args:
            entity: The domain Book entity.

        Returns:
            A BookModel instance ready for database persistence.
        """
        return BookModel(
            id=entity.id,
            name=entity.name,
            author=entity.author,
            url=entity.url,
            description=entity.description,
            content=entity.content,
        )
