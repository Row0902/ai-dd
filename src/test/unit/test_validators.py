"""Unit tests for domain validators: protocol and concrete validators.

.. note::
   Since ``Book`` now composes value objects (``BookName``, ``BookAuthor``,
   ``BookUrl``) that validate eagerly on construction, individual validators
   operating on an already-constructed ``Book`` will always pass — the value
   objects guarantee that the entity is in a valid state.

   Validators remain for the **Composite / Strategy pattern** so they can be
   injected into use cases as a composable validation boundary.  Error-case
   coverage for individual fields lives in ``test_value_objects.py`` and
   ``test_domain_entities.py``.  This file covers validator instantiation,
   protocol compliance, and the happy-path contract.

   CompositeValidator tests are in ``test_composite_validator.py``.
"""

from __future__ import annotations

from domain.validators import Validator
from domain.validators.book_author import BookAuthorValidator
from domain.validators.book_name import BookNameValidator
from domain.validators.book_url import BookUrlValidator

from .conftest import _valid_book

# ---------------------------------------------------------------------------
# Protocol compliance
# ---------------------------------------------------------------------------


class TestValidatorProtocol:
    """Test ``Validator[T]`` protocol compliance."""

    def test_validator_is_abstract_base(self) -> None:
        """``Validator`` defines an abstract ``validate`` method."""
        assert hasattr(Validator, "validate")

    def test_book_name_validator_is_a_validator(self) -> None:
        """``BookNameValidator`` satisfies the ``Validator`` protocol."""
        assert isinstance(BookNameValidator(), Validator)

    def test_book_author_validator_is_a_validator(self) -> None:
        """``BookAuthorValidator`` satisfies the ``Validator`` protocol."""
        assert isinstance(BookAuthorValidator(), Validator)

    def test_book_url_validator_is_a_validator(self) -> None:
        """``BookUrlValidator`` satisfies the ``Validator`` protocol."""
        assert isinstance(BookUrlValidator(), Validator)


# ---------------------------------------------------------------------------
# BookNameValidator — happy path
# ---------------------------------------------------------------------------


class TestBookNameValidator:
    """All validator tests use only valid Books (VOs guarantee validity)."""

    def test_valid_name_returns_empty_list(self) -> None:
        """A valid name produces no validation errors."""
        book = _valid_book(name="Clean Code")
        assert BookNameValidator().validate(book) == []

    def test_name_with_whitespace_returns_empty_list(self) -> None:
        """Whitespace-trimmed name is valid (stripped by BookName VO)."""
        book = _valid_book(name="  Refactoring  ")
        assert BookNameValidator().validate(book) == []

    def test_long_name_within_limit_returns_empty_list(self) -> None:
        """A name at the 200-character limit is valid."""
        book = _valid_book(name="A" * 200)
        assert BookNameValidator().validate(book) == []


# ---------------------------------------------------------------------------
# BookAuthorValidator — happy path
# ---------------------------------------------------------------------------


class TestBookAuthorValidator:
    """Test ``BookAuthorValidator`` with valid Books."""

    def test_valid_author_returns_empty_list(self) -> None:
        """A valid author produces no validation errors."""
        book = _valid_book(author="Kent Beck")
        assert BookAuthorValidator().validate(book) == []

    def test_empty_author_returns_empty_list(self) -> None:
        """Empty author is a valid optional field."""
        book = _valid_book(author="")
        assert BookAuthorValidator().validate(book) == []

    def test_author_within_limit_returns_empty_list(self) -> None:
        """An author at the 150-character limit is valid."""
        book = _valid_book(author="A" * 150)
        assert BookAuthorValidator().validate(book) == []


# ---------------------------------------------------------------------------
# BookUrlValidator — happy path
# ---------------------------------------------------------------------------


class TestBookUrlValidator:
    """Test ``BookUrlValidator`` with valid Books."""

    def test_valid_url_returns_empty_list(self) -> None:
        """A valid URL produces no validation errors."""
        book = _valid_book(url="https://example.com/book")
        assert BookUrlValidator().validate(book) == []

    def test_empty_url_returns_empty_list(self) -> None:
        """Empty URL is a valid optional field."""
        book = _valid_book(url="")
        assert BookUrlValidator().validate(book) == []

    def test_http_scheme_url_returns_empty_list(self) -> None:
        """An HTTP-scheme URL passes validation."""
        book = _valid_book(url="http://example.com")
        assert BookUrlValidator().validate(book) == []
