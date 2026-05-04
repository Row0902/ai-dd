"""Validator protocol: generic abstract interface for domain validation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from domain.exceptions import ValidationError

T = TypeVar("T")


class Validator(ABC, Generic[T]):
    """Abstract base class for domain validators.

    Concrete validators implement `validate(entity)` and return
    a list of `ValidationError` items. An empty list means valid.
    """

    @abstractmethod
    def validate(self, entity: T) -> list[ValidationError]:
        """Validate the given entity.

        Args:
            entity: The domain object to validate.

        Returns:
            List of validation errors. Empty if valid.
        """
