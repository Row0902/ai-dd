"""JSON serializer for Book entities.

Converts between Book domain objects and plain dicts suitable for JSON
storage.  Extracted from ``JsonBookRepository`` to follow the Single
Responsibility Principle.
"""

from __future__ import annotations

from typing import Any

from domain.entities import Book
from domain.exceptions import DomainError


def dict_to_book(item: dict[str, Any]) -> Book:
    """Convert a raw dict to a Book entity.

    Args:
        item: Dictionary with book data from JSON storage.

    Returns:
        Book entity.

    Raises:
        DomainError: When required fields are missing or have wrong types.
    """
    book_id = item.get("id")
    name = item.get("name")
    if not isinstance(book_id, str):
        raise DomainError("Book entry missing or invalid 'id' field")
    if not isinstance(name, str):
        raise DomainError("Book entry missing or invalid 'name' field")

    author = item.get("author")
    description = item.get("description")
    url = item.get("url")
    content = item.get("content")
    return Book(
        id=book_id,
        name=name,
        author=author if isinstance(author, str) else "",
        description=description if isinstance(description, str) else "",
        url=url if isinstance(url, str) else "",
        content=content if isinstance(content, str) else "",
    )


def book_to_dict(book: Book) -> dict[str, str]:
    """Convert a Book entity to a plain dict for JSON storage.

    Args:
        book: Book entity.

    Returns:
        Dictionary with all book fields as strings.
    """
    return {
        "id": book.id,
        "name": book.name,
        "author": book.author,
        "description": book.description,
        "url": book.url,
        "content": book.content,
    }
