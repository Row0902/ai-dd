"""Create book use case.

Handles book creation with optional domain validation.
"""

from __future__ import annotations

from domain.entities import Book
from domain.exceptions import AggregatedValidationError
from domain.repositories import BookRepository
from domain.validators.protocol import Validator


async def create_book(
    repo: BookRepository,
    *,
    name: str,
    author: str = "",
    description: str = "",
    url: str = "",
    content: str = "",
    validator: Validator[Book] | None = None,
) -> Book:
    """Create a book.

    ID generation is delegated to the repository adapter (e.g. JSON repo).

    Args:
        repo: Repository port.
        name: Book title.
        author: Author name.
        description: Description.
        url: Reference URL.
        content: Content/summary.
        validator: Optional domain validator. When provided, the draft is
            validated before persistence. On failure, raises DomainError.

    Returns:
        Persisted book entity.

    Raises:
        DomainError: When validator is provided and validation fails.
    """
    draft = Book(
        id="",
        name=name,
        author=author,
        description=description,
        url=url,
        content=content,
    )
    _validate_or_raise(validator, draft)
    return await repo.create(draft)


def _validate_or_raise(validator: Validator[Book] | None, draft: Book) -> None:
    """Run validator on draft and raise on errors.

    A single ``ValidationError`` is raised directly for the common one-error
    case.  Multiple errors (e.g. from a ``CompositeValidator``) are wrapped in
    ``ValidationErrors`` so that every failure reaches the caller.

    Args:
        validator: Optional validator instance.
        draft: Book entity to validate.

    Raises:
        ValidationError: When a single validation rule fails.
        AggregatedValidationError: When multiple validation rules fail.
    """
    if validator is None:
        return
    errors = validator.validate(draft)
    if not errors:
        return
    if len(errors) == 1:
        raise errors[0]
    raise AggregatedValidationError(errors)
