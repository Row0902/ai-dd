"""List books use case.

Returns all books from the repository.
"""

from __future__ import annotations

from domain.entities import Book
from domain.repositories import BookRepository


async def list_books(
    repo: BookRepository, limit: int = 20, offset: int = 0
) -> list[Book]:
    """Return books with pagination.

    Args:
        repo: Repository port.
        limit: Maximum number of books to return (default 20).
        offset: Number of books to skip (default 0).

    Returns:
        Paginated list of books.
    """
    return await repo.list(limit=limit, offset=offset)
