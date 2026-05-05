"""List books use case.

Returns all books from the repository.
"""

from __future__ import annotations

from domain.entities import Book
from domain.repositories import BookRepository


def list_books(repo: BookRepository) -> list[Book]:
    """Return all books.

    Args:
        repo: Repository port.

    Returns:
        List of all books.
    """
    return repo.list()
