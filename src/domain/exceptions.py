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
