"""Read book use case.

Retrieves a single book by its identifier.
"""

from __future__ import annotations

from domain.entities import Book
from domain.repositories import BookRepository


def get_book(repo: BookRepository, book_id: str) -> Book | None:
    """Return a book by its ID.

    Args:
        repo: Repository port.
        book_id: Book identifier.

    Returns:
        The book if found, otherwise None.
    """
    return repo.get(book_id)
