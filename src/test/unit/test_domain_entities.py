"""Unit tests for domain entities."""

import pytest

from domain.entities import Book
from domain.exceptions import ValidationError


class TestBookEntity:
    """Test Book dataclass instantiation and properties."""

    def test_book_creation_minimal(self) -> None:
        """Test creating a Book with minimal fields."""
        book = Book(id="abc123", name="Python Guide")
        assert book.id == "abc123"
        assert book.name == "Python Guide"
        assert book.author == ""
        assert book.description == ""
        assert book.url == ""
        assert book.content == ""

    def test_book_creation_full(self) -> None:
        """Test creating a Book with all fields."""
        book = Book(
            id="xyz789",
            name="Clean Code",
            author="Robert C. Martin",
            description="A Handbook of Agile Software Craftsmanship",
            url="https://example.com/clean-code",
            content="Full book content here...",
        )
        assert book.id == "xyz789"
        assert book.name == "Clean Code"
        assert book.author == "Robert C. Martin"
        assert book.description == "A Handbook of Agile Software Craftsmanship"
        assert book.url == "https://example.com/clean-code"
        assert book.content == "Full book content here..."

    def test_book_dataclass_equality(self) -> None:
        """Test Book equality by field values."""
        book1 = Book(id="same", name="Test")
        book2 = Book(id="same", name="Test")
        assert book1 == book2

    def test_book_dataclass_inequality(self) -> None:
        """Test Book inequality when fields differ."""
        book1 = Book(id="id1", name="Test")
        book2 = Book(id="id2", name="Test")
        assert book1 != book2

    def test_book_field_types(self) -> None:
        """Test that Book fields are of expected types."""
        book = Book(id="123", name="Title")
        assert isinstance(book.id, str)
        assert isinstance(book.name, str)
        assert isinstance(book.author, str)
        assert isinstance(book.description, str)
        assert isinstance(book.url, str)
        assert isinstance(book.content, str)


class TestBookValidation:
    """Test Book entity validates fields via value objects in __post_init__."""

    def test_empty_name_raises_validation_error(self) -> None:
        """Book with empty name raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Book(id="1", name="")
        assert exc_info.value.field == "name"

    def test_whitespace_only_name_raises_validation_error(self) -> None:
        """Book with whitespace-only name raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Book(id="1", name="   ")
        assert exc_info.value.field == "name"

    def test_name_too_long_raises_validation_error(self) -> None:
        """Book with name exceeding 200 chars raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Book(id="1", name="A" * 201)
        assert exc_info.value.field == "name"

    def test_name_trimmed_on_construction(self) -> None:
        """Book trims surrounding whitespace from name."""
        book = Book(id="1", name="  Clean Code  ")
        assert book.name == "Clean Code"

    def test_valid_name_accepted(self) -> None:
        """Book with valid name is accepted."""
        book = Book(id="1", name="Clean Code")
        assert book.name == "Clean Code"

    def test_empty_author_allowed_default(self) -> None:
        """Book with empty author (default) is accepted for backward compat."""
        book = Book(id="1", name="Clean Code")
        assert book.author == ""

    def test_empty_url_allowed_default(self) -> None:
        """Book with empty url (default) is accepted for backward compat."""
        book = Book(id="1", name="Clean Code")
        assert book.url == ""

    def test_valid_url_accepted(self) -> None:
        """Book with valid URL is accepted."""
        book = Book(id="1", name="Clean Code", url="https://example.com")
        assert book.url == "https://example.com"

    def test_invalid_url_raises_validation_error(self) -> None:
        """Book with malformed URL raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Book(id="1", name="Clean Code", url="not-a-url")
        assert exc_info.value.field == "url"

    def test_author_too_long_raises_validation_error(self) -> None:
        """Book with author exceeding 150 chars raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Book(id="1", name="Clean Code", author="A" * 151)
        assert exc_info.value.field == "author"

    def test_whitespace_author_stripped(self) -> None:
        """Book trims surrounding whitespace from author."""
        book = Book(id="1", name="Clean Code", author="  Robert  ")
        assert book.author == "Robert"
