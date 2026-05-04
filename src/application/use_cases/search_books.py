"""Search books use case.

Searches books by name using repository-level matching semantics.
"""

from __future__ import annotations

from domain.entities import Book
from domain.repositories import BookRepository


async def get_books_by_name(repo: BookRepository, name: str) -> list[Book]:
    """Search books by name.

    Delegates search semantics to the repository port.

    Args:
        repo: Repository port.
        name: Search term.

    Returns:
        List of matching books.
    """
    return await repo.get_by_name(name)
