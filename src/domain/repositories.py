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
    def list(self) -> builtins.list[Book]:
        """List all books.

        Returns:
            List of all Book entities.
        """

    @abstractmethod
    def get(self, book_id: str) -> Book | None:
        """Get a book by ID.

        Args:
            book_id: Unique identifier of the book.

        Returns:
            Book if found, None otherwise.
        """

    @abstractmethod
    def get_by_name(self, name: str) -> builtins.list[Book]:
        """Search books by name (case-insensitive substring match).

        Args:
            name: Search term.

        Returns:
            List of books whose name contains the search term.
        """

    @abstractmethod
    def create(self, book: Book) -> Book:
        """Create a new book.

        Args:
            book: Book entity to create.

        Returns:
            Created book (with persisted state).
        """

    @abstractmethod
    def update(self, book_id: str, book: Book) -> Book | None:
        """Update an existing book.

        Args:
            book_id: Unique identifier of the book to update.
            book: Updated book data.

        Returns:
            Updated book if found, None otherwise.
        """

    @abstractmethod
    def delete(self, book_id: str) -> bool:
        """Delete a book.

        Args:
            book_id: Unique identifier of the book to delete.

        Returns:
            True if deleted, False if not found.
        """
