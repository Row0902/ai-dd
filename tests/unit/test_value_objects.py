"""Unit tests for domain value objects: BookName, BookAuthor, BookUrl."""

import pytest

from domain.exceptions import ValidationError
from domain.value_objects.book_author import BookAuthor
from domain.value_objects.book_name import BookName
from domain.value_objects.book_url import BookUrl


class TestBookName:
    """Test BookName value object: frozen, validates non-empty, <=200 chars."""

    def test_valid_name_construction(self) -> None:
        """BookName stores the value and is hashable."""
        name = BookName("Clean Code")
        assert name.value == "Clean Code"
        assert isinstance(hash(name), int)

    def test_strips_whitespace(self) -> None:
        """BookName trims surrounding whitespace on construction."""
        name = BookName("  Clean Code  ")
        assert name.value == "Clean Code"

    def test_empty_string_raises(self) -> None:
        """BookName raises ValidationError for empty string."""
        with pytest.raises(ValidationError) as exc_info:
            BookName("")
        assert exc_info.value.field == "name"

    def test_whitespace_only_raises(self) -> None:
        """BookName raises ValidationError for whitespace-only string."""
        with pytest.raises(ValidationError) as exc_info:
            BookName("   ")
        assert exc_info.value.field == "name"

    def test_too_long_raises(self) -> None:
        """BookName raises ValidationError for name > 200 chars."""
        with pytest.raises(ValidationError) as exc_info:
            BookName("A" * 201)
        assert exc_info.value.field == "name"
        assert "200" in exc_info.value.message

    def test_exactly_200_chars_passes(self) -> None:
        """BookName accepts exactly 200 characters."""
        name = BookName("A" * 200)
        assert len(name.value) == 200

    def test_equality_by_value(self) -> None:
        """Two BookNames with same value are equal."""
        assert BookName("Clean Code") == BookName("Clean Code")

    def test_inequality_by_value(self) -> None:
        """Two BookNames with different values are not equal."""
        assert BookName("Clean Code") != BookName("Dirty Code")

    def test_same_value_same_hash(self) -> None:
        """Equal BookNames have the same hash."""
        assert hash(BookName("Clean Code")) == hash(BookName("Clean Code"))

    def test_immutability(self) -> None:
        """BookName is immutable (frozen dataclass)."""
        name = BookName("Clean Code")
        with pytest.raises(AttributeError):
            name.value = "other"  # ty: ignore[invalid-assignment]


class TestBookAuthor:
    """Test BookAuthor value object: frozen, validates non-empty, <=150 chars."""

    def test_valid_author_construction(self) -> None:
        """BookAuthor stores the value and is hashable."""
        author = BookAuthor("Robert C. Martin")
        assert author.value == "Robert C. Martin"
        assert isinstance(hash(author), int)

    def test_strips_whitespace(self) -> None:
        """BookAuthor trims surrounding whitespace."""
        author = BookAuthor("  Robert C. Martin  ")
        assert author.value == "Robert C. Martin"

    def test_empty_string_raises(self) -> None:
        """BookAuthor raises ValidationError for empty string."""
        with pytest.raises(ValidationError) as exc_info:
            BookAuthor("")
        assert exc_info.value.field == "author"

    def test_whitespace_only_raises(self) -> None:
        """BookAuthor raises ValidationError for whitespace-only string."""
        with pytest.raises(ValidationError) as exc_info:
            BookAuthor("   ")
        assert exc_info.value.field == "author"

    def test_too_long_raises(self) -> None:
        """BookAuthor raises ValidationError for author > 150 chars."""
        with pytest.raises(ValidationError) as exc_info:
            BookAuthor("A" * 151)
        assert exc_info.value.field == "author"
        assert "150" in exc_info.value.message

    def test_exactly_150_chars_passes(self) -> None:
        """BookAuthor accepts exactly 150 characters."""
        author = BookAuthor("A" * 150)
        assert len(author.value) == 150

    def test_equality_by_value(self) -> None:
        """Two BookAuthors with same value are equal."""
        assert BookAuthor("Bob") == BookAuthor("Bob")

    def test_immutability(self) -> None:
        """BookAuthor is immutable (frozen dataclass)."""
        author = BookAuthor("Bob")
        with pytest.raises(AttributeError):
            author.value = "other"  # ty: ignore[invalid-assignment]


class TestBookUrl:
    """Test BookUrl value object: frozen, validates URL format, <=2048 chars."""

    def test_valid_url_construction(self) -> None:
        """BookUrl stores the value and is hashable."""
        url = BookUrl("https://example.com/book")
        assert url.value == "https://example.com/book"
        assert isinstance(hash(url), int)

    def test_malformed_url_raises(self) -> None:
        """BookUrl raises ValidationError for malformed URL."""
        with pytest.raises(ValidationError) as exc_info:
            BookUrl("not-a-url")
        assert exc_info.value.field == "url"
        assert "Invalid URL format" in exc_info.value.message

    def test_empty_string_raises(self) -> None:
        """BookUrl raises ValidationError for empty string."""
        with pytest.raises(ValidationError) as exc_info:
            BookUrl("")
        assert exc_info.value.field == "url"

    def test_too_long_raises(self) -> None:
        """BookUrl raises ValidationError for URL > 2048 chars."""
        with pytest.raises(ValidationError) as exc_info:
            BookUrl("https://example.com/" + "a" * 2049)
        assert exc_info.value.field == "url"
        assert "2048" in exc_info.value.message

    def test_http_scheme_passes(self) -> None:
        """BookUrl accepts HTTP URLs."""
        url = BookUrl("http://example.com")
        assert url.value == "http://example.com"

    def test_equality_by_value(self) -> None:
        """Two BookUrls with same value are equal."""
        assert BookUrl("https://example.com") == BookUrl("https://example.com")

    def test_immutability(self) -> None:
        """BookUrl is immutable (frozen dataclass)."""
        url = BookUrl("https://example.com")
        with pytest.raises(AttributeError):
            url.value = "other"  # ty: ignore[invalid-assignment]
