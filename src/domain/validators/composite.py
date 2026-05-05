"""CompositeValidator: runs all validators, aggregates errors into flat list."""

from __future__ import annotations

from typing import override

from domain.exceptions import ValidationError
from domain.validators.protocol import Validator


class CompositeValidator[T](Validator[T]):
    """Aggregates multiple validators into a single flat validation pass.

    Runs all validators (no short-circuit) and collects all errors.
    """

    def __init__(self, validators: list[Validator[T]]) -> None:
        """Initialize with a flat list of validators.

        Args:
            validators: Validators to run. No nesting — flat list only.
        """
        self._validators = validators

    @override
    def validate(self, entity: T) -> list[ValidationError]:
        """Run all validators and aggregate errors.

        Args:
            entity: The domain object to validate.

        Returns:
            Flat list of all validation errors from all validators.
        """
        errors: list[ValidationError] = []
        for validator in self._validators:
            errors.extend(validator.validate(entity))
        return errors
