"""Delete book use case.

Removes a book from the repository.
"""

from __future__ import annotations

from domain.repositories import BookRepository


async def delete_book(repo: BookRepository, book_id: str) -> bool:
    """Delete a book.

    Args:
        repo: Repository port.
        book_id: Book identifier.

    Returns:
        True if deleted, False if not found.
    """
    return await repo.delete(book_id)
