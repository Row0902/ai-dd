"""In-memory book repository for testing.

Dict-backed, thread-safe implementation of ``BookRepository``.
Intended for unit tests and as the default backend when
``DATABASE_URL`` is unset (``memory://``).
"""

from __future__ import annotations

import builtins
import threading
import uuid
from typing import override

from domain.entities import Book
from domain.repositories import BookRepository


class InMemoryBookRepository(BookRepository):
    """BookRepository backed by an in-memory dict.

    Thread-safe: all mutating operations acquire a lock.
    """

    def __init__(self) -> None:
        """Initialize an empty in-memory store."""
        self._books: dict[str, Book] = {}
        self._lock = threading.Lock()

    @override
    async def list(self, limit: int = 20, offset: int = 0) -> builtins.list[Book]:
        """List books with pagination.

        Args:
            limit: Maximum number of books to return.
            offset: Number of books to skip.

        Returns:
            Paginated list of Book entities.
        """
        books = list(self._books.values())
        return books[offset : offset + limit]

    @override
    async def get(self, book_id: str) -> Book | None:
        """Get a book by ID.

        Args:
            book_id: Unique identifier.

        Returns:
            Book if found, None otherwise.
        """
        return self._books.get(book_id)

    @override
    async def get_by_name(self, name: str) -> builtins.list[Book]:
        """Search books by case-insensitive substring match on name.

        Args:
            name: Search term.

        Returns:
            Matching books.
        """
        needle = name.lower()
        return [b for b in self._books.values() if needle in b.name.lower()]

    @override
    async def create(self, book: Book) -> Book:
        """Create a new book.

        If the passed entity has an empty id, assign a UUID4 hex id.

        Args:
            book: Book entity to create.

        Returns:
            Created book with persisted id.
        """
        with self._lock:
            created = Book(
                id=book.id or uuid.uuid4().hex,
                name=book.name,
                author=book.author,
                description=book.description,
                url=book.url,
                content=book.content,
            )
            self._books[created.id] = created
            return created

    @override
    async def update(self, book_id: str, book: Book) -> Book | None:
        """Update an existing book.

        Args:
            book_id: ID of the book to update.
            book: Replacement book data (id is ignored).

        Returns:
            Updated book if found, None otherwise.
        """
        with self._lock:
            if book_id not in self._books:
                return None
            updated = Book(
                id=book_id,
                name=book.name,
                author=book.author,
                description=book.description,
                url=book.url,
                content=book.content,
            )
            self._books[book_id] = updated
            return updated

    @override
    async def delete(self, book_id: str) -> bool:
        """Delete a book by id.

        Args:
            book_id: ID of the book to delete.

        Returns:
            True if deleted, False if not found.
        """
        with self._lock:
            if book_id in self._books:
                del self._books[book_id]
                return True
            return False
