"""BookUrlValidator: validates URL format using urllib.parse."""

from typing import override
from urllib.parse import urlparse

from domain.entities import Book
from domain.exceptions import ValidationError
from domain.validation_rules import MAX_URL_LENGTH
from domain.validators.protocol import Validator


class BookUrlValidator(Validator[Book]):
    """Validates the url field of a Book entity."""

    @override
    def validate(self, entity: Book) -> list[ValidationError]:
        """Validate that the book URL is well-formed and within length limits."""
        errors: list[ValidationError] = []
        if not entity.url:
            return errors
        if len(entity.url) > MAX_URL_LENGTH:
            errors.append(
                ValidationError(
                    field="url",
                    message=f"URL exceeds {MAX_URL_LENGTH} characters",
                )
            )
            return errors
        parsed = urlparse(entity.url)
        if not parsed.scheme or not parsed.netloc:
            errors.append(ValidationError(field="url", message="Invalid URL format"))
        return errors
