"""NoOp rate limiter: always allows requests (fail-open / testing fallback)."""

from __future__ import annotations

from domain.rate_limiting.ports import RateLimiter


class NoOpRateLimiter(RateLimiter):
    """Rate limiter that always allows requests.

    Used as a fallback when Redis is unavailable or rate limiting is disabled
    (``RATE_LIMIT_ENABLED=False`` or ``DATABASE_URL=memory://``).
    """

    async def check(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Always allow the request.

        Args:
            key: Rate limit key (ignored).
            max_requests: Maximum requests (ignored).
            window_seconds: Window duration (ignored).

        Returns:
            Always True.
        """
        return True

    async def reset(self, key: str) -> None:
        """No-op reset.

        Args:
            key: Rate limit key (ignored).
        """
