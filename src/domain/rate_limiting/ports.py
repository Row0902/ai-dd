"""Rate limiting domain ports: abstract interfaces for rate limit adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod


class RateLimiter(ABC):
    """Port for rate limiting operations.

    Implementations may use Redis Sorted Sets (sliding window),
    in-memory counters, or no-ops for testing/fail-open.
    """

    @abstractmethod
    async def check(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if a request is allowed under the rate limit.

        Args:
            key: Unique identifier for the rate limit scope (e.g., IP + path).
            max_requests: Maximum requests allowed in the window.
            window_seconds: Duration of the sliding window in seconds.

        Returns:
            True if the request is allowed, False if the limit is exceeded.
        """

    @abstractmethod
    async def reset(self, key: str) -> None:
        """Reset the rate limit counter for a given key.

        Args:
            key: The rate limit key to reset.
        """
