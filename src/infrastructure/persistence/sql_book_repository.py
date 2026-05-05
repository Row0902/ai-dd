"""SQL-backed book repository implementation.

Implements the ``BookRepository`` port using async SQLAlchemy sessions and
the Data Mapper pattern (``BookMapper``). All persistence goes through
the ``BookModel`` SQLModel table — domain ``Book`` entities are never
directly persisted.
"""

from __future__ import annotations

import builtins
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import Book
from domain.repositories import BookRepository
from infrastructure.persistence.book_mapper import BookMapper
from infrastructure.persistence.sql_models import BookModel


class SQLBookRepository(BookRepository):
    """BookRepository backed by a SQL database via async SQLAlchemy.

    Uses the Data Mapper pattern: domain Book ↔ BookModel translation
    is handled by ``BookMapper``. The session is injected via constructor
    for testability and per-request scoping.

    Args:
        session: An AsyncSession instance.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with an async database session.

        Args:
            session: Active async SQLAlchemy session for database operations.
        """
        self._session = session

    async def list(self, limit: int = 20, offset: int = 0) -> builtins.list[Book]:
        """List books with SQL LIMIT/OFFSET pagination.

        Args:
            limit: Maximum number of books to return (default 20).
            offset: Number of books to skip (default 0).

        Returns:
            Paginated list of domain Book entities.
        """
        statement = select(BookModel).offset(offset).limit(limit)
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [BookMapper.to_domain(m) for m in models]

    async def get(self, book_id: str) -> Book | None:
        """Get a book by ID.

        Args:
            book_id: Unique identifier of the book.

        Returns:
            Book if found, None otherwise.
        """
        model = await self._session.get(BookModel, book_id)
        if model is None:
            return None
        return BookMapper.to_domain(model)

    async def get_by_name(self, name: str) -> builtins.list[Book]:
        """Search books by case-insensitive substring match on name.

        Uses SQL LOWER() + LIKE for case-insensitive matching.

        Args:
            name: Search term.

        Returns:
            List of matching domain Book entities.
        """
        needle = f"%{name.lower()}%"
        statement = select(BookModel).where(func.lower(BookModel.name).like(needle))
        result = await self._session.execute(statement)
        models = result.scalars().all()
        return [BookMapper.to_domain(m) for m in models]

    async def create(self, book: Book) -> Book:
        """Create a new book.

        If the entity has an empty id, a UUID4 hex id is generated.

        Args:
            book: Book entity to create.

        Returns:
            Created book with persisted state.
        """
        book_id = book.id or uuid.uuid4().hex
        model = BookMapper.to_model(
            Book(
                id=book_id,
                name=book.name,
                author=book.author,
                description=book.description,
                url=book.url,
                content=book.content,
            )
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return BookMapper.to_domain(model)

    async def update(self, book_id: str, book: Book) -> Book | None:
        """Update an existing book.

        Args:
            book_id: ID of the book to update.
            book: Replacement book data (id is ignored).

        Returns:
            Updated book if found, None otherwise.
        """
        model = await self._session.get(BookModel, book_id)
        if model is None:
            return None
        model.name = book.name
        model.author = book.author
        model.description = book.description
        model.url = book.url
        model.content = book.content
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return BookMapper.to_domain(model)

    async def delete(self, book_id: str) -> bool:
        """Delete a book by id.

        Args:
            book_id: ID of the book to delete.

        Returns:
            True if deleted, False if not found.
        """
        model = await self._session.get(BookModel, book_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True
