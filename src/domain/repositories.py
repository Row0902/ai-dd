"""Domain ports: abstract interfaces for persistence adapters."""

from __future__ import annotations

import builtins
from abc import ABC, abstractmethod

from domain.entities import Book


class BookRepository(ABC):
    """Port for book persistence.

    Abstract interface defining the contract that any concrete repository
    (e.g., JSON-based, database-based) must implement.
    """

    @abstractmethod
    async def list(
        self, limit: int = 20, offset: int = 0
    ) -> builtins.list[Book]:
        """List books with pagination.

        Args:
            limit: Maximum number of books to return (default 20).
            offset: Number of books to skip (default 0).

        Returns:
            List of Book entities for the requested page.
        """

    @abstractmethod
    async def get(self, book_id: str) -> Book | None:
        """Get a book by ID.

        Args:
            book_id: Unique identifier of the book.

        Returns:
            Book if found, None otherwise.
        """

    @abstractmethod
    async def get_by_name(self, name: str) -> builtins.list[Book]:
        """Search books by name (case-insensitive substring match).

        Args:
            name: Search term.

        Returns:
            List of books whose name contains the search term.
        """

    @abstractmethod
    async def create(self, book: Book) -> Book:
        """Create a new book.

        Args:
            book: Book entity to create.

        Returns:
            Created book (with persisted state).
        """

    @abstractmethod
    async def update(self, book_id: str, book: Book) -> Book | None:
        """Update an existing book.

        Args:
            book_id: Unique identifier of the book to update.
            book: Updated book data.

        Returns:
            Updated book if found, None otherwise.
        """

    @abstractmethod
    async def delete(self, book_id: str) -> bool:
        """Delete a book.

        Args:
            book_id: Unique identifier of the book to delete.

        Returns:
            True if deleted, False if not found.
        """
