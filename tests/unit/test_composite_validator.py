"""Unit tests for CompositeValidator: aggregation, delegation, spy verification.

.. note::
   Since ``Book`` now composes value objects that validate eagerly on
   construction, individual validators operating on an already-constructed
   ``Book`` will always pass.  This file focuses on the composite structure:
   delegation to all validators, empty-list handling, and spy-based call
   verification.
"""

from __future__ import annotations

from domain.entities import Book
from domain.validators import Validator
from domain.validators.book_author import BookAuthorValidator
from domain.validators.book_name import BookNameValidator
from domain.validators.book_url import BookUrlValidator
from domain.validators.composite import CompositeValidator

from .conftest import _valid_book


class TestCompositeValidator:
    """Test ``CompositeValidator`` aggregation and delegation."""

    # -- empty / single -----------------------------------------------------

    def test_empty_validator_list_returns_no_errors(self) -> None:
        """A composite with no validators always returns an empty list."""
        composite = CompositeValidator[Book](validators=[])
        assert composite.validate(_valid_book()) == []

    def test_single_passing_validator_returns_no_errors(self) -> None:
        """A composite with one passing validator returns no errors."""
        composite = CompositeValidator[Book](validators=[BookNameValidator()])
        assert composite.validate(_valid_book()) == []

    # -- all validators pass ------------------------------------------------

    def test_all_validators_pass_returns_empty(self) -> None:
        """When all validators pass, the composite returns an empty list."""
        composite = CompositeValidator[Book](
            validators=[
                BookNameValidator(),
                BookAuthorValidator(),
                BookUrlValidator(),
            ]
        )
        assert composite.validate(_valid_book()) == []

    # -- composite structure ------------------------------------------------

    def test_composite_iterates_all_validators(self) -> None:
        """Even when all pass, every validator in the list is called."""
        calls: list[str] = []

        class SpyValidator(Validator[Book]):
            """Validator that records calls for spying on composite delegation."""

            def __init__(self, tag: str) -> None:
                """Initialize with a tag to record in the calls list."""
                self.tag = tag

            def validate(self, entity: Book) -> list:  # type: ignore[override]
                """Record this validator's tag and return no errors."""
                calls.append(self.tag)
                return []

        composite = CompositeValidator[Book](
            validators=[SpyValidator("a"), SpyValidator("b"), SpyValidator("c")]
        )
        composite.validate(_valid_book())
        assert calls == ["a", "b", "c"]
