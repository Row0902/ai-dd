"""Tests for infrastructure.persistence.book_mapper: BookMapper."""

from __future__ import annotations

from domain.entities import Book
from infrastructure.persistence.book_mapper import BookMapper
from infrastructure.persistence.sql_models import BookModel


class TestBookMapperToDomain:
    """Tests for BookMapper.to_domain() — BookModel → Book."""

    def test_to_domain_converts_all_fields(self):
        """to_domain should map all BookModel fields to Book entity."""
        model = BookModel(
            id="b1",
            name="Clean Code",
            author="Robert C. Martin",
            description="A Handbook",
            url="https://example.com",
            content="Chapter 1",
        )
        book = BookMapper.to_domain(model)
        assert book.id == "b1"
        assert book.name == "Clean Code"
        assert book.author == "Robert C. Martin"
        assert book.description == "A Handbook"
        assert book.url == "https://example.com"
        assert book.content == "Chapter 1"

    def test_to_domain_reconstructs_value_objects(self):
        """to_domain should reconstruct BookName, BookAuthor, BookUrl VOs."""
        model = BookModel(
            id="b1",
            name="DDD",
            author="Evans",
            url="https://ddd.com",
        )
        book = BookMapper.to_domain(model)
        # Accessing .name, .author, .url proves VOs were reconstructed
        assert book.name == "DDD"
        assert book.author == "Evans"
        assert book.url == "https://ddd.com"

    def test_to_domain_handles_empty_optional_fields(self):
        """to_domain should handle empty strings for author and url."""
        model = BookModel(id="b1", name="Test")
        book = BookMapper.to_domain(model)
        assert book.author == ""
        assert book.url == ""
        assert book.description == ""
        assert book.content == ""


class TestBookMapperToModel:
    """Tests for BookMapper.to_model() — Book → BookModel."""

    def test_to_model_converts_all_fields(self):
        """to_model should map all Book fields to BookModel."""
        book = Book(
            id="b1",
            name="Clean Code",
            author="Martin",
            description="Desc",
            url="https://example.com",
            content="Content",
        )
        model = BookMapper.to_model(book)
        assert model.id == "b1"
        assert model.name == "Clean Code"
        assert model.author == "Martin"
        assert model.description == "Desc"
        assert model.url == "https://example.com"
        assert model.content == "Content"

    def test_to_model_handles_empty_optional_fields(self):
        """to_model should handle Book with empty author and url."""
        book = Book(id="b1", name="Test")
        model = BookMapper.to_model(book)
        assert model.author == ""
        assert model.url == ""


class TestBookMapperRoundTrip:
    """Round-trip tests: Book → BookModel → Book should preserve data."""

    def test_round_trip_preserves_all_fields(self):
        """Book → BookModel → Book should yield equal entity."""
        original = Book(
            id="b1",
            name="Clean Code",
            author="Robert C. Martin",
            description="A Handbook",
            url="https://example.com",
            content="Chapter 1",
        )
        model = BookMapper.to_model(original)
        restored = BookMapper.to_domain(model)
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.author == original.author
        assert restored.description == original.description
        assert restored.url == original.url
        assert restored.content == original.content

    def test_round_trip_preserves_special_characters(self):
        """Round-trip should handle special characters in fields."""
        original = Book(
            id="b1",
            name="El Quijote — edición especial",
            author="Cervantes, Miguel de",
            description="Descripción con acentos: ñ, ü, é",
            url="https://example.com/path?q=1&r=2",
            content="Contenido con 'comillas' y \"dobles\"",
        )
        model = BookMapper.to_model(original)
        restored = BookMapper.to_domain(model)
        assert restored.name == original.name
        assert restored.author == original.author
        assert restored.description == original.description
        assert restored.url == original.url
        assert restored.content == original.content

    def test_round_trip_with_minimal_fields(self):
        """Round-trip with only required fields should work."""
        original = Book(id="b1", name="Minimal")
        model = BookMapper.to_model(original)
        restored = BookMapper.to_domain(model)
        assert restored.id == "b1"
        assert restored.name == "Minimal"
        assert restored.author == ""
        assert restored.url == ""
