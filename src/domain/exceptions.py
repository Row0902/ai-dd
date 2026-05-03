"""Domain exceptions: base error hierarchy for the domain layer."""

from dataclasses import dataclass


class DomainError(Exception):
    """Base exception for all domain-layer errors."""


@dataclass(eq=True)
class ValidationError(DomainError):
    """A single field-level validation error.

    PERMANENT CONSTRAINT — NOT frozen:
    Python 3.14+ frozen dataclasses disallow ``__setattr__`` entirely, but
    ``Exception`` needs to set ``__traceback__`` during propagation at the C
    level. Using ``frozen=True`` on an Exception subclass causes a runtime
    ``AttributeError`` when the exception is raised.

    This class uses ``eq=True`` plus a manual ``__hash__`` to achieve the same
    value semantics (hashable, comparable by field values) without blocking
    ``Exception`` internals.

    Attributes:
        field: The name of the field that failed validation.
        message: Human-readable description of the validation failure.
    """

    field: str
    message: str

    def __str__(self) -> str:
        """Return a readable string representation."""
        return f"{self.field}: {self.message}"

    def __hash__(self) -> int:
        """Make ValidationError hashable based on field values."""
        return hash((self.field, self.message))


class AggregatedValidationError(DomainError):
    """Multiple aggregated field-level validation errors.

    Raised when a ``CompositeValidator`` (or any multi-validator) collects
    more than one error.  Carries the full list so that consumers — such as
    the HTTP exception handler — can report every failure at once.

    A single ``ValidationError`` is still raised directly for the common
    one-error case, preserving backward compatibility with existing callers.

    Attributes:
        errors: The aggregated list of ``ValidationError`` instances
            (guaranteed non-empty at construction time).
    """

    def __init__(self, errors: list[ValidationError]) -> None:
        """Initialize with a non-empty list of validation errors.

        Args:
            errors: At least one ``ValidationError`` instance.

        Raises:
            ValueError: If ``errors`` is empty.
        """
        if not errors:
            raise ValueError("AggregatedValidationError requires at least one error")
        self.errors = errors
        super().__init__(str(errors[0]))
