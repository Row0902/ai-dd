"""Replace book use case.

Handles full replacement of an existing book (PUT semantics) with optional
domain validation.
"""

from __future__ import annotations

from domain.entities import Book
from domain.repositories import BookRepository
from domain.validators.protocol import Validator

from .create_book import _validate_or_raise


async def replace_book(
    repo: BookRepository,
    book_id: str,
    *,
    name: str,
    author: str = "",
    description: str = "",
    url: str = "",
    content: str = "",
    validator: Validator[Book] | None = None,
) -> Book | None:
    """Replace an existing book with a full new representation.

    This matches PUT semantics: unspecified fields are not preserved; instead they
    are replaced with provided values (or defaults).

    Args:
        repo: Repository port.
        book_id: Book identifier.
        name: Book title.
        author: Author name.
        description: Description.
        url: Reference URL.
        content: Content/summary.
        validator: Optional domain validator. When provided, the replacement
            book is validated before persistence. On failure, raises DomainError.

    Returns:
        Replaced book if found, otherwise None.

    Raises:
        DomainError: When validator is provided and validation fails.
    """
    replacement = Book(
        id=book_id,
        name=name,
        author=author,
        description=description,
        url=url,
        content=content,
    )
    _validate_or_raise(validator, replacement)
    return await repo.update(book_id, replacement)
