"""Shared test utilities for unit tests."""

from __future__ import annotations

from domain.entities import Book


def _valid_book(**overrides: str) -> Book:
    """Return a fully-valid ``Book`` for validator happy-path tests."""
    defaults: dict[str, str] = {
        "id": "1",
        "name": "Clean Code",
        "author": "Robert C. Martin",
        "url": "https://example.com/book",
    }
    return Book(**(defaults | overrides))
