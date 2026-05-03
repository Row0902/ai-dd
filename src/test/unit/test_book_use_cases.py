"""Unit tests for application-layer book use cases."""

from __future__ import annotations

import builtins

from application.use_cases.book_use_case import (
    create_book,
    delete_book,
    get_book,
    get_books_by_name,
    list_books,
    replace_book,
    update_book,
)
from domain.entities import Book
from domain.repositories import BookRepository


class InMemoryBookRepository(BookRepository):
    """Simple in-memory repository for unit tests."""

    def __init__(self) -> None:
        """Initialize empty in-memory store."""
        self._books: dict[str, Book] = {}
        self._next_id = 1

    def list(self) -> builtins.list[Book]:
        """List all books."""
        return list(self._books.values())

    def get(self, book_id: str) -> Book | None:
        """Get book by id."""
        return self._books.get(book_id)

    def get_by_name(self, name: str) -> builtins.list[Book]:
        """Case-insensitive substring match on name."""
        needle = name.lower()
        return [b for b in self._books.values() if needle in b.name.lower()]

    def create(self, book: Book) -> Book:
        """Persist a new book (assign id if missing)."""
        book_id = book.id or f"id-{self._next_id}"
        self._next_id += 1
        created = Book(
            id=book_id,
            name=book.name,
            author=book.author,
            url=book.url,
            description=book.description,
            content=book.content,
        )
        self._books[book_id] = created
        return created

    def update(self, book_id: str, book: Book) -> Book | None:
        """Update an existing book."""
        if book_id not in self._books:
            return None
        updated = Book(
            id=book_id,
            name=book.name,
            author=book.author,
            url=book.url,
            description=book.description,
            content=book.content,
        )
        self._books[book_id] = updated
        return updated

    def delete(self, book_id: str) -> bool:
        """Delete book by id."""
        return self._books.pop(book_id, None) is not None


class TestBookUseCases:
    """Tests for use case functions."""

    def test_list_books_empty(self) -> None:
        """Listing on empty repository returns an empty list."""
        repo = InMemoryBookRepository()
        assert list_books(repo) == []

    def test_create_book_assigns_id_and_persists(self) -> None:
        """Create returns persisted book with assigned id."""
        repo = InMemoryBookRepository()
        created = create_book(repo, name="Clean Code", author="Robert C. Martin")
        assert created.id
        assert created.name == "Clean Code"
        assert created.author == "Robert C. Martin"
        assert repo.get(created.id) == created

    def test_get_book_missing_returns_none(self) -> None:
        """Get returns None for unknown id."""
        repo = InMemoryBookRepository()
        assert get_book(repo, "does-not-exist") is None

    def test_get_books_by_name_is_case_insensitive_substring(self) -> None:
        """Search is case-insensitive and matches substrings."""
        repo = InMemoryBookRepository()
        repo.create(Book(id="", name="Clean Code"))
        repo.create(Book(id="", name="The Clean Coder"))
        repo.create(Book(id="", name="Domain-Driven Design"))
        res = get_books_by_name(repo, "cLeAn")
        assert sorted([b.name for b in res]) == ["Clean Code", "The Clean Coder"]

    def test_update_book_partial_merges_fields(self) -> None:
        """Update merges only provided fields and keeps others."""
        repo = InMemoryBookRepository()
        created = repo.create(
            Book(
                id="",
                name="Clean Code",
                author="Bob",
                description="d",
                url="https://example.com/book",
            )
        )
        updated = update_book(repo, created.id, author="Robert", content="c")
        assert updated is not None
        assert updated.id == created.id
        assert updated.name == "Clean Code"
        assert updated.author == "Robert"
        assert updated.description == "d"
        assert updated.url == "https://example.com/book"
        assert updated.content == "c"

    def test_replace_book_overwrites_unspecified_fields(self) -> None:
        """Replace overwrites all fields (PUT semantics), not a merge."""
        repo = InMemoryBookRepository()
        created = repo.create(
            Book(
                id="",
                name="Old",
                author="Old Author",
                description="Old desc",
                url="https://example.com/old",
                content="old-content",
            )
        )

        replaced = replace_book(repo, created.id, name="New")
        assert replaced is not None
        assert replaced.id == created.id
        assert replaced.name == "New"
        assert replaced.author == ""
        assert replaced.description == ""
        assert replaced.url == ""
        assert replaced.content == ""

    def test_replace_book_missing_returns_none(self) -> None:
        """Replace returns None if the book doesn't exist."""
        repo = InMemoryBookRepository()
        assert replace_book(repo, "missing", name="X") is None

    def test_update_book_missing_returns_none(self) -> None:
        """Update returns None if the book doesn't exist."""
        repo = InMemoryBookRepository()
        assert update_book(repo, "missing", name="New") is None

    def test_delete_book_returns_true_when_deleted(self) -> None:
        """Delete returns True when deletion succeeds."""
        repo = InMemoryBookRepository()
        created = repo.create(Book(id="", name="Clean Architecture"))
        assert delete_book(repo, created.id) is True
        assert repo.get(created.id) is None

    def test_delete_book_returns_false_when_missing(self) -> None:
        """Delete returns False when id is not found."""
        repo = InMemoryBookRepository()
        assert delete_book(repo, "missing") is False
