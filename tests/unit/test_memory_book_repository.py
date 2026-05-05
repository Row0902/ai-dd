"""Tests for infrastructure.memory_book_repository: InMemoryBookRepository."""

import threading

from domain.entities import Book
from infrastructure.memory_book_repository import InMemoryBookRepository


class TestInMemoryBookRepositoryCreate:
    """Tests for create() method."""

    async def test_create_returns_book_with_id(self):
        """Create returns a Book with a generated id."""
        repo = InMemoryBookRepository()
        book = await repo.create(Book(id="", name="Clean Code", author="Martin"))
        assert book.id
        assert book.name == "Clean Code"
        assert book.author == "Martin"

    async def test_create_preserves_existing_id(self):
        """Create preserves the id if one is already set."""
        repo = InMemoryBookRepository()
        book = await repo.create(Book(id="custom-id", name="DDD", author="Evans"))
        assert book.id == "custom-id"


class TestInMemoryBookRepositoryGet:
    """Tests for get() method."""

    async def test_get_returns_book_when_found(self):
        """get() returns the book when it exists."""
        repo = InMemoryBookRepository()
        created = await repo.create(Book(id="b1", name="Test"))
        found = await repo.get("b1")
        assert found is not None
        assert found.id == created.id

    async def test_get_returns_none_when_not_found(self):
        """get() returns None for a nonexistent id."""
        repo = InMemoryBookRepository()
        assert await repo.get("nonexistent") is None


class TestInMemoryBookRepositoryGetByName:
    """Tests for get_by_name() method."""

    async def test_get_by_name_case_insensitive_substring(self):
        """get_by_name matches case-insensitive substrings."""
        repo = InMemoryBookRepository()
        await repo.create(Book(id="1", name="Clean Code"))
        await repo.create(Book(id="2", name="The Clean Coder"))
        await repo.create(Book(id="3", name="DDD"))
        results = await repo.get_by_name("cLeAn")
        assert sorted(b.name for b in results) == ["Clean Code", "The Clean Coder"]

    async def test_get_by_name_no_match(self):
        """get_by_name returns empty list when nothing matches."""
        repo = InMemoryBookRepository()
        await repo.create(Book(id="1", name="Clean Code"))
        assert await repo.get_by_name("Python") == []


class TestInMemoryBookRepositoryList:
    """Tests for list() with pagination."""

    async def _create_books(self, repo: InMemoryBookRepository, count: int):
        for i in range(count):
            await repo.create(Book(id=f"b{i:02d}", name=f"Book {i:02d}"))

    async def test_list_returns_all_when_fewer_than_limit(self):
        """list() returns all books when fewer than limit exist."""
        repo = InMemoryBookRepository()
        await self._create_books(repo, 5)
        assert len(await repo.list()) == 5

    async def test_list_limit_caps_results(self):
        """list(limit=3) returns at most 3 books."""
        repo = InMemoryBookRepository()
        await self._create_books(repo, 10)
        books = await repo.list(limit=3)
        assert len(books) == 3

    async def test_list_offset_skips_books(self):
        """list(offset=2) skips the first 2 books."""
        repo = InMemoryBookRepository()
        await self._create_books(repo, 5)
        books = await repo.list(offset=2)
        assert len(books) == 3
        assert books[0].id == "b02"

    async def test_list_limit_and_offset_together(self):
        """list(limit=2, offset=3) returns books at index 3 and 4."""
        repo = InMemoryBookRepository()
        await self._create_books(repo, 10)
        books = await repo.list(limit=2, offset=3)
        assert len(books) == 2
        assert books[0].id == "b03"
        assert books[1].id == "b04"

    async def test_list_offset_beyond_end_returns_empty(self):
        """list(offset=100) on a 5-book repo returns empty list."""
        repo = InMemoryBookRepository()
        await self._create_books(repo, 5)
        assert await repo.list(offset=100) == []


class TestInMemoryBookRepositoryUpdate:
    """Tests for update() method."""

    async def test_update_replaces_book(self):
        """update() replaces the existing book data."""
        repo = InMemoryBookRepository()
        await repo.create(Book(id="b1", name="Old"))
        updated = await repo.update("b1", Book(id="ignored", name="New", author="A"))
        assert updated is not None
        assert updated.id == "b1"
        assert updated.name == "New"
        assert updated.author == "A"

    async def test_update_returns_none_when_not_found(self):
        """update() returns None for a nonexistent id."""
        repo = InMemoryBookRepository()
        assert await repo.update("nope", Book(id="x", name="X")) is None


class TestInMemoryBookRepositoryDelete:
    """Tests for delete() method."""

    async def test_delete_returns_true_when_found(self):
        """delete() returns True and removes the book."""
        repo = InMemoryBookRepository()
        await repo.create(Book(id="b1", name="To Delete"))
        assert await repo.delete("b1") is True
        assert await repo.get("b1") is None

    async def test_delete_returns_false_when_not_found(self):
        """delete() returns False for a nonexistent id."""
        repo = InMemoryBookRepository()
        assert await repo.delete("nonexistent") is False


class TestInMemoryBookRepositoryThreadSafety:
    """Verify thread-safe operations with concurrent access."""

    async def test_concurrent_creates(self):
        """Multiple threads can create books concurrently."""
        repo = InMemoryBookRepository()
        errors: list[Exception] = []

        def create_book(idx: int):
            try:
                import asyncio

                loop = asyncio.new_event_loop()
                loop.run_until_complete(
                    repo.create(Book(id=f"t{idx}", name=f"Thread {idx}"))
                )
                loop.close()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_book, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(await repo.list(limit=100)) == 20
