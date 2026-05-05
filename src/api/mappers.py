"""Mapping helpers between domain entities and HTTP JSON shapes."""

from __future__ import annotations

from domain.entities import Book


def book_to_dict(book: Book) -> dict[str, str]:
    """Convert a domain Book entity to the HTTP JSON representation."""
    return {
        "id": book.id,
        "name": book.name,
        "author": book.author,
        "description": book.description,
        "url": book.url,
        "content": book.content,
    }
