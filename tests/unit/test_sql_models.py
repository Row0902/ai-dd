"""Tests for infrastructure.persistence.sql_models: BookModel."""

from __future__ import annotations

from sqlmodel import SQLModel

from infrastructure.persistence.sql_models import BookModel


class TestBookModelTableConfig:
    """Verify BookModel is a valid SQLModel table with correct schema."""

    def test_book_model_is_sqlmodel_table(self):
        """BookModel should be a SQLModel with table=True."""
        assert BookModel.__tablename__ == "books"

    def test_book_model_has_id_primary_key(self):
        """BookModel.id should be the primary key column."""
        pk_cols = [
            col.name
            for col in BookModel.__table__.primary_key.columns  # type: ignore[attr-defined]
        ]
        assert pk_cols == ["id"]

    def test_book_model_has_all_required_columns(self):
        """BookModel should have id, name, author, description, url, content."""
        expected = {"id", "name", "author", "description", "url", "content"}
        actual = {col.name for col in BookModel.__table__.columns}  # type: ignore[attr-defined]
        assert actual == expected

    def test_book_model_defaults(self):
        """BookModel fields except id and name should default to empty string."""
        model = BookModel(id="1", name="Test")
        assert model.author == ""
        assert model.description == ""
        assert model.url == ""
        assert model.content == ""

    def test_book_model_all_fields_accept_strings(self):
        """BookModel should accept string values for all fields."""
        model = BookModel(
            id="abc-123",
            name="Clean Code",
            author="Robert C. Martin",
            description="A Handbook",
            url="https://example.com",
            content="Chapter 1...",
        )
        assert model.id == "abc-123"
        assert model.name == "Clean Code"
        assert model.author == "Robert C. Martin"
        assert model.description == "A Handbook"
        assert model.url == "https://example.com"
        assert model.content == "Chapter 1..."

    def test_book_model_is_sqlmodel_subclass(self):
        """BookModel should be a subclass of SQLModel."""
        assert issubclass(BookModel, SQLModel)
