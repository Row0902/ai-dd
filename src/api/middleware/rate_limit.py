"""Rate limit middleware: dependency factory for per-endpoint rate limiting."""

from __future__ import annotations

import time

from fastapi import Depends, Request
from fastapi.responses import Response

from api.dependencies import get_rate_limiter, get_settings
from config.settings import AppSettings
from domain.rate_limiting.exceptions import RateLimitExceededError
from domain.rate_limiting.ports import RateLimiter


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


async def _enforce_rate_limit(
    request: Request,
    response: Response,
    limiter: RateLimiter,
    max_requests: int,
    window_seconds: int,
) -> None:
    """Core rate limit enforcement logic.

    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
        limiter: The rate limiter implementation.
        max_requests: Maximum requests allowed in the window.
        window_seconds: Duration of the sliding window in seconds.

    Raises:
        RateLimitExceededError: If the client exceeds the rate limit.
    """
    client_ip = _extract_client_ip(request)
    key = f"rate_limit:{client_ip}:{request.url.path}"
    allowed = await limiter.check(
        key=key,
        max_requests=max_requests,
        window_seconds=window_seconds,
    )

    response.headers["RateLimit-Limit"] = str(max_requests)
    response.headers["RateLimit-Reset"] = str(int(time.time()) + window_seconds)

    if not allowed:
        response.headers["RateLimit-Remaining"] = "0"
        raise RateLimitExceededError(
            retry_after=window_seconds,
            limit=max_requests,
        )

    response.headers["RateLimit-Remaining"] = str(max_requests - 1)


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

    async def dependency(
        request: Request,
        response: Response,
        limiter: RateLimiter = Depends(get_rate_limiter),
    ) -> None:
        """Check rate limit and set response headers.

        Args:
            request: The incoming HTTP request.
            response: The outgoing HTTP response (for setting headers).
            limiter: Rate limiter implementation (injected by FastAPI).

        Raises:
            RateLimitExceededError: If the client exceeds the rate limit.
        """
        await _enforce_rate_limit(request, response, limiter, max_requests, window_seconds)

    return dependency


async def login_rate_limit(
    request: Request,
    response: Response,
    settings: AppSettings = Depends(get_settings),
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> None:
    """Rate limit dependency for POST /auth/login.

    Reads limits from application settings.

    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
        settings: Application settings.
        limiter: Rate limiter implementation.

    Raises:
        RateLimitExceededError: If the client exceeds the rate limit.
    """
    await _enforce_rate_limit(
        request, response, limiter,
        settings.RATE_LIMIT_LOGIN_MAX,
        settings.RATE_LIMIT_LOGIN_WINDOW,
    )


async def register_rate_limit(
    request: Request,
    response: Response,
    settings: AppSettings = Depends(get_settings),
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> None:
    """Rate limit dependency for POST /auth/register.

    Reads limits from application settings.

    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
        settings: Application settings.
        limiter: Rate limiter implementation.

    Raises:
        RateLimitExceededError: If the client exceeds the rate limit.
    """
    await _enforce_rate_limit(
        request, response, limiter,
        settings.RATE_LIMIT_REGISTER_MAX,
        settings.RATE_LIMIT_REGISTER_WINDOW,
    )


async def global_rate_limit(
    request: Request,
    response: Response,
    settings: AppSettings = Depends(get_settings),
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> None:
    """Rate limit dependency for global endpoint rate limiting.

    Reads limits from application settings.

    Args:
        request: The incoming HTTP request.
        response: The outgoing HTTP response.
        settings: Application settings.
        limiter: Rate limiter implementation.

    Raises:
        RateLimitExceededError: If the client exceeds the rate limit.
    """
    await _enforce_rate_limit(
        request, response, limiter,
        settings.RATE_LIMIT_GLOBAL_MAX,
        settings.RATE_LIMIT_GLOBAL_WINDOW,
    )
