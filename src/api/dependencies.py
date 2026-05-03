"""Dependency providers for the API layer."""

from __future__ import annotations

from domain.repositories import BookRepository


def get_book_repo() -> BookRepository:
    """Provide a BookRepository implementation.

    The composition root (e.g. `main.create_app`) must override this dependency.
    """
    raise RuntimeError("BookRepository provider not configured")
