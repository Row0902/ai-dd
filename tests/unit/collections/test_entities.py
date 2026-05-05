"""Unit tests for Collection domain entity."""

from __future__ import annotations

from datetime import UTC, datetime

from domain.collections.entities import Collection


class TestCollectionEntity:
    """Tests for Collection dataclass construction and defaults."""

    def test_collection_construction_with_all_fields(self) -> None:
        """Collection stores all provided fields correctly."""
        now = datetime.now(UTC)
        c = Collection(
            id="abc123",
            name="My Books",
            description="Favorite technical books",
            owner_id="user-1",
            book_ids=["b1", "b2"],
            created_at=now,
            updated_at=now,
        )
        assert c.id == "abc123"
        assert c.name == "My Books"
        assert c.description == "Favorite technical books"
        assert c.owner_id == "user-1"
        assert c.book_ids == ["b1", "b2"]
        assert c.created_at == now
        assert c.updated_at == now

    def test_collection_defaults(self) -> None:
        """Collection has sensible defaults for optional fields."""
        c = Collection(id="x", name="Test")
        assert c.description == ""
        assert c.owner_id == ""
        assert c.book_ids == []
        assert isinstance(c.created_at, datetime)
        assert isinstance(c.updated_at, datetime)

    def test_collection_book_ids_default_is_empty_list(self) -> None:
        """Each Collection gets its own empty list for book_ids (no shared mutable)."""
        c1 = Collection(id="1", name="A")
        c2 = Collection(id="2", name="B")
        c1.book_ids.append("book-x")
        assert c2.book_ids == []
