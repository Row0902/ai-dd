"""Book-related use cases.

These functions coordinate work using domain ports (repositories) and return
domain entities. They are framework-agnostic.
"""

from __future__ import annotations

from dataclasses import replace

from domain.entities import Book
from domain.repositories import BookRepository
from domain.validators.protocol import Validator


def list_books(repo: BookRepository) -> list[Book]:
    """Return all books.

    Args:
        repo: Repository port.

    Returns:
        List of all books.
    """
    return repo.list()


def get_book(repo: BookRepository, book_id: str) -> Book | None:
    """Return a book by its ID.

    Args:
        repo: Repository port.
        book_id: Book identifier.

    Returns:
        The book if found, otherwise None.
    """
    return repo.get(book_id)


def get_books_by_name(repo: BookRepository, name: str) -> list[Book]:
    """Search books by name.

    Delegates search semantics to the repository port.

    Args:
        repo: Repository port.
        name: Search term.

    Returns:
        List of matching books.
    """
    return repo.get_by_name(name)


def create_book(
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
    return repo.create(draft)


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


def replace_book(
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
    return repo.update(book_id, replacement)


def delete_book(repo: BookRepository, book_id: str) -> bool:
    """Delete a book.

    Args:
        repo: Repository port.
        book_id: Book identifier.

    Returns:
        True if deleted, False if not found.
    """
    return repo.delete(book_id)


def _validate_or_raise(validator: Validator[Book] | None, draft: Book) -> None:
    """Run validator on draft and raise DomainError if errors found.

    Args:
        validator: Optional validator instance.
        draft: Book entity to validate.

    Raises:
        DomainError: When validator returns one or more errors.
    """
    if validator is None:
        return
    errors = validator.validate(draft)
    if errors:
        raise errors[0]
