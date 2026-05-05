"""JSON file repository adapter.

Implements the domain `BookRepository` port using a local JSON file containing
an array of book objects (dicts).

Behavior intentionally mirrors the current monolith:
- Missing/corrupt file is treated as empty library.
- Full file is read/written per operation (simple kata-friendly approach).
"""

from __future__ import annotations

import builtins
import json
import logging
import threading
import uuid
from pathlib import Path
from typing import Any

from domain.entities import Book
from domain.exceptions import DomainError
from domain.repositories import BookRepository
from infrastructure.serializers.json_book_serializer import (
    book_to_dict as _book_to_dict,
)
from infrastructure.serializers.json_book_serializer import (
    dict_to_book as _dict_to_book_impl,
)

logger = logging.getLogger(__name__)


class JsonBookRepository(BookRepository):
    """BookRepository implementation backed by a JSON file."""

    def __init__(self, data_file: Path) -> None:
        """Create a repository using the given JSON file path."""
        self._data_file = data_file
        self._lock = threading.Lock()

    def list(self) -> builtins.list[Book]:
        """List all books."""
        return self._load_books()

    def get(self, book_id: str) -> Book | None:
        """Get a book by id."""
        for book in self._load_books():
            if book.id == book_id:
                return book
        return None

    def get_by_name(self, name: str) -> builtins.list[Book]:
        """Search books by case-insensitive substring match on name."""
        needle = name.lower()
        return [b for b in self._load_books() if needle in b.name.lower()]

    def create(self, book: Book) -> Book:
        """Create a new book.

        If the passed entity has an empty id, assign a UUID4 hex id.
        """
        with self._lock:
            books = self._load_books_unlocked()
            created = Book(
                id=book.id or uuid.uuid4().hex,
                name=book.name,
                author=book.author,
                description=book.description,
                url=book.url,
                content=book.content,
            )
            books.append(created)
            self._save_books_unlocked(books)
            return created

    def update(self, book_id: str, book: Book) -> Book | None:
        """Update an existing book.

        The passed `book` is treated as a full representation; its id is ignored
        and replaced with `book_id`.
        """
        with self._lock:
            books = self._load_books_unlocked()
            for idx, existing in enumerate(books):
                if existing.id == book_id:
                    updated = Book(
                        id=book_id,
                        name=book.name,
                        author=book.author,
                        description=book.description,
                        url=book.url,
                        content=book.content,
                    )
                    books[idx] = updated
                    self._save_books_unlocked(books)
                    return updated
            return None

    def delete(self, book_id: str) -> bool:
        """Delete a book by id."""
        with self._lock:
            books = self._load_books_unlocked()
            for idx, existing in enumerate(books):
                if existing.id == book_id:
                    books.pop(idx)
                    self._save_books_unlocked(books)
                    return True
            return False

    def _load_books(self) -> builtins.list[Book]:
        with self._lock:
            return self._load_books_unlocked()

    def _load_books_unlocked(self) -> builtins.list[Book]:
        data = self._load_raw()
        books: list[Book] = []
        for item in data:
            try:
                book = _dict_to_book_impl(item)
                books.append(book)
            except DomainError:
                logger.warning("Skipping malformed book entry: %s", item)
        return books

    def _save_books_unlocked(self, books: builtins.list[Book]) -> None:
        self._save_raw([_book_to_dict(b) for b in books])

    def _load_raw(self) -> builtins.list[dict[str, Any]]:
        if not self._data_file.exists():
            return []

        try:
            data = json.loads(self._data_file.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return []
            return [x for x in data if isinstance(x, dict)]
        except Exception:
            return []

    def _save_raw(self, data: builtins.list[dict[str, Any]]) -> None:
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(data, indent=2, ensure_ascii=False)

        # Atomic write: write temp file then replace.
        tmp = self._data_file.with_suffix(self._data_file.suffix + ".tmp")
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(self._data_file)

    @staticmethod
    def _dict_to_book(item: dict[str, Any]) -> Book:
        """Convert a raw dict to a Book entity.

        Delegates to :func:`infrastructure.serializers.json_book_serializer.dict_to_book`.

        Args:
            item: Dictionary with book data from JSON storage.

        Returns:
            Book entity.

        Raises:
            DomainError: When required fields are missing or have wrong types.
        """
        return _dict_to_book_impl(item)

    @staticmethod
    def _book_to_dict(book: Book) -> dict[str, str]:
        """Convert a Book entity to a dict.

        Delegates to :func:`infrastructure.serializers.json_book_serializer.book_to_dict`.
        """
        return _book_to_dict(book)
