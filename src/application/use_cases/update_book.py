"""Update book use case.

Handles partial updates to an existing book with optional domain validation.
"""

from __future__ import annotations

from dataclasses import replace

from domain.entities import Book
from domain.repositories import BookRepository
from domain.validators.protocol import Validator

from .create_book import _validate_or_raise


def update_book(
    repo: BookRepository,
    book_id: str,
    *,
    name: str | None = None,
    author: str | None = None,
    description: str | None = None,
    url: str | None = None,
    content: str | None = None,
    validator: Validator[Book] | None = None,
) -> Book | None:
    """Update an existing book.

    This supports partial updates at the use case level. The HTTP layer can
    still enforce full-body updates if needed.

    Args:
        repo: Repository port.
        book_id: Book identifier.
        name: New name (optional).
        author: New author (optional).
        description: New description (optional).
        url: New URL (optional).
        content: New content (optional).
        validator: Optional domain validator. When provided, the updated book
            is validated before persistence. On failure, raises DomainError.

    Returns:
        Updated book if found, otherwise None.

    Raises:
        DomainError: When validator is provided and validation fails.
    """
    current = repo.get(book_id)
    if current is None:
        return None

    updated = replace(
        current,
        name=current.name if name is None else name,
        author=current.author if author is None else author,
        description=current.description if description is None else description,
        url=current.url if url is None else url,
        content=current.content if content is None else content,
    )
    _validate_or_raise(validator, updated)
    return repo.update(book_id, updated)
