"""Rate limiting domain exceptions."""

from __future__ import annotations

from dataclasses import dataclass

from domain.exceptions import DomainError


@dataclass(eq=True)
class RateLimitExceededError(DomainError):
    """Raised when a client exceeds the rate limit for an endpoint.

    PERMANENT CONSTRAINT — NOT frozen:
    Python 3.14+ frozen dataclasses disallow ``__setattr__`` entirely, but
    ``Exception`` needs to set ``__traceback__`` during propagation at the C
    level. Using ``frozen=True`` on an Exception subclass causes a runtime
    ``AttributeError`` when the exception is raised.

    This class uses ``eq=True`` plus a manual ``__hash__`` to achieve the same
    value semantics (hashable, comparable by field values) without blocking
    ``Exception`` internals.

    Attributes:
        retry_after: Seconds until the client may retry the request.
        limit: Maximum requests allowed in the window (for response headers).
    """

    retry_after: int
    limit: int

    def __str__(self) -> str:
        """Return a readable string representation."""
        return f"Rate limit exceeded. Retry after {self.retry_after} seconds."

    def __hash__(self) -> int:
        """Make RateLimitExceededError hashable based on fields."""
        return hash((self.retry_after, self.limit))
