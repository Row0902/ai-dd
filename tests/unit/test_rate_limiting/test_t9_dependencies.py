"""T9: Unit tests for get_redis_client() and get_rate_limiter() dependency providers."""

from __future__ import annotations

from unittest.mock import patch

from config.settings import AppSettings
from domain.rate_limiting.ports import RateLimiter
from infrastructure.rate_limiting.noop_rate_limiter import NoOpRateLimiter
from infrastructure.rate_limiting.redis_rate_limiter import RedisRateLimiter

TEST_SECRET = "test-secret-key-at-least-32-chars-long"


class TestGetRedisClient:
    """Tests for get_redis_client() provider."""

    def _reset_singleton(self) -> None:
        """Reset singletons for test isolation."""
        import api.dependencies as deps
        deps._settings = None
        deps._rate_limiter = None

    def test_returns_redis_client(self) -> None:
        """Provider returns a Redis client from settings REDIS_URL."""
        from api.dependencies import get_redis_client

        self._reset_singleton()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            REDIS_URL="redis://localhost:6379/0",
        )
        with patch("api.dependencies.get_settings", return_value=settings):
            client = get_redis_client()
        assert client is not None

    def test_returns_async_redis_instance(self) -> None:
        """Provider returns redis.asyncio.Redis instance."""
        import redis.asyncio

        from api.dependencies import get_redis_client

        self._reset_singleton()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
        )
        with patch("api.dependencies.get_settings", return_value=settings):
            client = get_redis_client()
        assert isinstance(client, redis.asyncio.Redis)


class TestGetRateLimiter:
    """Tests for get_rate_limiter() provider."""

    def _reset_singleton(self) -> None:
        """Reset the rate limiter singleton for test isolation."""
        import api.dependencies as deps
        deps._rate_limiter = None

    def teardown_method(self) -> None:
        """Clean up after each test."""
        self._reset_singleton()

    def test_returns_noop_when_disabled(self) -> None:
        """Returns NoOpRateLimiter when RATE_LIMIT_ENABLED=False."""
        from api.dependencies import get_rate_limiter

        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=False,
        )
        with patch("api.dependencies.get_settings", return_value=settings):
            limiter = get_rate_limiter()
        assert isinstance(limiter, NoOpRateLimiter)
        assert isinstance(limiter, RateLimiter)

    def test_returns_noop_when_memory_database(self) -> None:
        """Returns NoOpRateLimiter when DATABASE_URL=memory://."""
        from api.dependencies import get_rate_limiter

        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
        )
        with patch("api.dependencies.get_settings", return_value=settings):
            limiter = get_rate_limiter()
        assert isinstance(limiter, NoOpRateLimiter)

    def test_returns_redis_limiter_when_enabled(self) -> None:
        """Returns RedisRateLimiter when RATE_LIMIT_ENABLED=True and not memory://."""
        from api.dependencies import get_rate_limiter

        settings = AppSettings(
            DATABASE_URL="sqlite:///test.db",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
            REDIS_URL="redis://localhost:6379/0",
        )
        with patch("api.dependencies.get_settings", return_value=settings):
            limiter = get_rate_limiter()
        assert isinstance(limiter, RedisRateLimiter)
        assert isinstance(limiter, RateLimiter)

    def test_singleton_returns_same_instance(self) -> None:
        """Subsequent calls return the same limiter instance."""
        from api.dependencies import get_rate_limiter

        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
        )
        with patch("api.dependencies.get_settings", return_value=settings):
            limiter1 = get_rate_limiter()
            limiter2 = get_rate_limiter()
        assert limiter1 is limiter2
