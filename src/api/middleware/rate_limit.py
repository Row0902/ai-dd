"""Rate limit middleware: dependency factory for per-endpoint rate limiting."""

from __future__ import annotations

import time

from fastapi import Request
from fastapi.responses import Response

from api.dependencies import get_rate_limiter
from domain.rate_limiting.exceptions import RateLimitExceededError


def _extract_client_ip(request: Request) -> str:
    """Extract the client IP from the request.

    Uses ``X-Forwarded-For`` header (first entry) when behind a proxy,
    falls back to ``request.client.host``.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The client IP address as a string.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return "unknown"


def require_rate_limit(max_requests: int, window_seconds: int):
    """Create a FastAPI dependency that enforces rate limiting.

    Mirrors the ``require_permission()`` pattern: returns an async dependency
    function compatible with ``Depends()``.

    Args:
        max_requests: Maximum requests allowed in the window.
        window_seconds: Duration of the sliding window in seconds.

    Returns:
        An async dependency function.
    """

    async def dependency(request: Request, response: Response) -> None:
        """Check rate limit and set response headers.

        Args:
            request: The incoming HTTP request.
            response: The outgoing HTTP response (for setting headers).

        Raises:
            RateLimitExceededError: If the client exceeds the rate limit.
        """
        limiter = get_rate_limiter()
        client_ip = _extract_client_ip(request)
        key = f"rate_limit:{client_ip}:{request.url.path}"
        allowed = await limiter.check(
            key=key,
            max_requests=max_requests,
            window_seconds=window_seconds,
        )

        # Set headers on every response
        response.headers["RateLimit-Limit"] = str(max_requests)
        response.headers["RateLimit-Reset"] = str(int(time.time()) + window_seconds)

        if not allowed:
            response.headers["RateLimit-Remaining"] = "0"
            raise RateLimitExceededError(retry_after=window_seconds)

        response.headers["RateLimit-Remaining"] = str(max_requests - 1)

    return dependency
