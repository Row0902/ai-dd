"""T14/T16/T18: Integration tests for rate limiting behavior.

Tests real rate limiting with TestClient using a counting rate limiter
to verify 429 responses, headers, fail-open, and key isolation.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from api.dependencies import get_rate_limiter
from config.settings import AppSettings
from domain.rate_limiting.ports import RateLimiter
from infrastructure.auth.jwt_token_service import JwtTokenService
from infrastructure.rate_limiting.redis_rate_limiter import RedisRateLimiter
from main import create_app

TEST_SECRET = "test-secret-key-at-least-32-chars-long"


class CountingRateLimiter(RateLimiter):
    """Rate limiter that tracks requests per key using in-memory counters.

    Simulates sliding window behavior for integration testing without Redis.
    """

    def __init__(self) -> None:
        """Initialize with empty counters."""
        self._counts: dict[str, list[float]] = {}

    async def check(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is allowed using in-memory sliding window.

        Args:
            key: Rate limit key.
            max_requests: Maximum requests in window.
            window_seconds: Window duration in seconds.

        Returns:
            True if allowed, False if limit exceeded.
        """
        now = time.time()
        window_start = now - window_seconds

        # Clean expired entries
        if key in self._counts:
            self._counts[key] = [t for t in self._counts[key] if t > window_start]
        else:
            self._counts[key] = []

        if len(self._counts[key]) >= max_requests:
            return False

        self._counts[key].append(now)
        return True

    async def reset(self, key: str) -> None:
        """Reset counter for a key.

        Args:
            key: Rate limit key to reset.
        """
        self._counts.pop(key, None)


def _auth_headers() -> dict[str, str]:
    """Create Authorization headers for a standard test user."""
    token_service = JwtTokenService(TEST_SECRET)
    token = token_service.generate("test-user-id", "user")
    return {"Authorization": f"Bearer {token}"}


def _client_with_limiter(
    limiter: RateLimiter,
    settings: AppSettings | None = None,
) -> TestClient:
    """Create a TestClient with a specific rate limiter override.

    Args:
        limiter: The rate limiter to use.
        settings: Optional settings override.

    Returns:
        Configured TestClient instance.
    """
    if settings is None:
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
        )
    app = create_app(settings)
    app.dependency_overrides[get_rate_limiter] = lambda: limiter
    return TestClient(app)


def _broken_limiter() -> RedisRateLimiter:
    """Create a RedisRateLimiter with broken Redis (fail-open test).

    The fail-open logic lives inside RedisRateLimiter.check() which catches
    all exceptions. We need a real RedisRateLimiter with a broken backend.
    """
    broken_redis = MagicMock()
    broken_redis.pipeline = MagicMock()
    mock_pipe = MagicMock()
    mock_pipe.zremrangebyscore = MagicMock(return_value=mock_pipe)
    mock_pipe.zcard = MagicMock(return_value=mock_pipe)
    mock_pipe.zadd = MagicMock(return_value=mock_pipe)
    mock_pipe.expire = MagicMock(return_value=mock_pipe)
    mock_pipe.execute = AsyncMock(side_effect=ConnectionError("Connection refused"))
    broken_redis.pipeline.return_value = mock_pipe
    return RedisRateLimiter(broken_redis)


class TestRateLimit429:
    """T14: Test that rate-limited endpoints return 429 when over limit."""

    def test_login_returns_429_when_rate_limited(self) -> None:
        """POST /auth/login returns 429 after exceeding rate limit."""
        limiter = CountingRateLimiter()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
            RATE_LIMIT_LOGIN_MAX=2,
            RATE_LIMIT_LOGIN_WINDOW=60,
        )
        client = _client_with_limiter(limiter, settings)

        # Make requests up to the limit (wrong password = 401, but counts)
        for _ in range(2):
            client.post(
                "/auth/login",
                json={"email": "test@example.com", "password": "wrong"},
            )

        # This one should be rate limited
        resp = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "wrong"},
        )
        assert resp.status_code == 429
        body = resp.json()
        assert body["detail"] == "Too many requests"

    def test_books_returns_429_when_rate_limited(self) -> None:
        """GET /books returns 429 after exceeding global rate limit."""
        limiter = CountingRateLimiter()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
            RATE_LIMIT_GLOBAL_MAX=2,
            RATE_LIMIT_GLOBAL_WINDOW=60,
        )
        client = _client_with_limiter(limiter, settings)
        headers = _auth_headers()

        # Exhaust the limit
        for _ in range(2):
            client.get("/books", headers=headers)

        # Should be rate limited
        resp = client.get("/books", headers=headers)
        assert resp.status_code == 429


class TestRateLimitHeaders:
    """T14: Test that rate limit headers are present on responses."""

    def test_429_includes_all_ietf_headers(self) -> None:
        """429 response includes Retry-After, RateLimit-Limit, RateLimit-Remaining, RateLimit-Reset."""
        limiter = CountingRateLimiter()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
            RATE_LIMIT_GLOBAL_MAX=1,
            RATE_LIMIT_GLOBAL_WINDOW=60,
        )
        client = _client_with_limiter(limiter, settings)
        headers = _auth_headers()

        # First request — allowed
        client.get("/books", headers=headers)

        # Second request — blocked
        resp = client.get("/books", headers=headers)
        assert resp.status_code == 429

        # Verify all 4 IETF headers
        assert "Retry-After" in resp.headers
        assert "RateLimit-Limit" in resp.headers
        assert "RateLimit-Remaining" in resp.headers
        assert "RateLimit-Reset" in resp.headers

        assert resp.headers["RateLimit-Limit"] == "1"
        assert resp.headers["RateLimit-Remaining"] == "0"
        assert int(resp.headers["Retry-After"]) > 0
        assert int(resp.headers["RateLimit-Reset"]) > 0

    def test_successful_response_includes_ratelimit_headers(self) -> None:
        """Successful (non-429) responses include RateLimit-* headers."""
        limiter = CountingRateLimiter()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
            RATE_LIMIT_GLOBAL_MAX=10,
            RATE_LIMIT_GLOBAL_WINDOW=60,
        )
        client = _client_with_limiter(limiter, settings)
        headers = _auth_headers()

        resp = client.get("/books", headers=headers)
        assert resp.status_code == 200

        # RateLimit headers should be present on successful responses
        assert "RateLimit-Limit" in resp.headers
        assert "RateLimit-Remaining" in resp.headers
        assert "RateLimit-Reset" in resp.headers
        assert resp.headers["RateLimit-Limit"] == "10"


class TestHealthExempt:
    """T14: Test that /health is never rate limited."""

    def test_health_not_rate_limited_even_under_load(self) -> None:
        """GET /health always returns 200 regardless of rate limit state."""
        limiter = CountingRateLimiter()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
            RATE_LIMIT_GLOBAL_MAX=1,
            RATE_LIMIT_GLOBAL_WINDOW=60,
        )
        client = _client_with_limiter(limiter, settings)
        headers = _auth_headers()

        # Exhaust rate limit on another endpoint
        client.get("/books", headers=headers)
        resp = client.get("/books", headers=headers)
        assert resp.status_code == 429

        # Health should still work — NO rate limit dependency
        for _ in range(10):
            resp = client.get("/health")
            assert resp.status_code == 200


class TestRateLimitWindowReset:
    """T14: Test that rate limiting resets after window expires."""

    def test_rate_limit_resets_after_window(self) -> None:
        """After the window expires, requests are allowed again."""
        limiter = CountingRateLimiter()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
            RATE_LIMIT_GLOBAL_MAX=2,
            RATE_LIMIT_GLOBAL_WINDOW=1,  # 1 second window for fast test
        )
        client = _client_with_limiter(limiter, settings)
        headers = _auth_headers()

        # Exhaust the limit
        client.get("/books", headers=headers)
        client.get("/books", headers=headers)
        resp = client.get("/books", headers=headers)
        assert resp.status_code == 429

        # Wait for the window to expire
        time.sleep(1.1)

        # Should be allowed again
        resp = client.get("/books", headers=headers)
        assert resp.status_code == 200


class TestFailOpen:
    """T16: Test fail-open behavior when Redis is unavailable."""

    def test_requests_succeed_when_redis_unavailable(self) -> None:
        """Requests pass through when limiter raises ConnectionError."""
        limiter = _broken_limiter()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
        )
        client = _client_with_limiter(limiter, settings)
        headers = _auth_headers()

        # All requests should succeed despite broken limiter
        for _ in range(10):
            resp = client.get("/books", headers=headers)
            assert resp.status_code == 200

    def test_login_succeeds_when_redis_unavailable(self) -> None:
        """Auth endpoints pass through when limiter is down."""
        limiter = _broken_limiter()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
        )
        client = _client_with_limiter(limiter, settings)

        # Login should succeed (may return 401 for wrong creds, but NOT 429)
        resp = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "wrong"},
        )
        assert resp.status_code != 429


class TestKeyIsolation:
    """T18: Test that rate limits are per-IP, per-endpoint."""

    def test_different_endpoints_independent_limits(self) -> None:
        """Rate limits on /books and /collections are independent."""
        limiter = CountingRateLimiter()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
            RATE_LIMIT_GLOBAL_MAX=1,
            RATE_LIMIT_GLOBAL_WINDOW=60,
        )
        client = _client_with_limiter(limiter, settings)
        headers = _auth_headers()

        # Exhaust limit on /books
        resp1 = client.get("/books", headers=headers)
        assert resp1.status_code == 200
        resp2 = client.get("/books", headers=headers)
        assert resp2.status_code == 429

        # /collections should still be available (different path = different key)
        resp3 = client.get("/collections", headers=headers)
        assert resp3.status_code == 200

    def test_different_ips_independent_limits(self) -> None:
        """Rate limits for different client IPs are independent."""
        limiter = CountingRateLimiter()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
            RATE_LIMIT_GLOBAL_MAX=1,
            RATE_LIMIT_GLOBAL_WINDOW=60,
        )
        client = _client_with_limiter(limiter, settings)

        # Exhaust limit for IP 1
        resp = client.get("/books", headers={
            **_auth_headers(),
            "X-Forwarded-For": "10.0.0.1",
        })
        assert resp.status_code == 200
        resp = client.get("/books", headers={
            **_auth_headers(),
            "X-Forwarded-For": "10.0.0.1",
        })
        assert resp.status_code == 429

        # Different IP should be allowed
        resp = client.get("/books", headers={
            **_auth_headers(),
            "X-Forwarded-For": "10.0.0.2",
        })
        assert resp.status_code == 200
