"""T6: Unit tests for Redis client factory."""

from __future__ import annotations

from config.settings import AppSettings
from infrastructure.rate_limiting.redis_client import create_redis_client


class TestCreateRedisClient:
    """Tests for create_redis_client factory function."""

    def test_returns_redis_client_from_settings_url(self) -> None:
        """Factory must create a Redis client from the REDIS_URL setting."""
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY="test-secret-key-at-least-32-chars-long",
            REDIS_URL="redis://localhost:6379/0",
        )
        client = create_redis_client(settings)
        assert client is not None

    def test_returns_client_with_custom_url(self) -> None:
        """Factory must accept custom REDIS_URL values."""
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY="test-secret-key-at-least-32-chars-long",
            REDIS_URL="redis://custom-host:6380/1",
        )
        client = create_redis_client(settings)
        assert client is not None

    def test_returns_async_redis_instance(self) -> None:
        """Factory must return a redis.asyncio.Redis instance."""
        import redis.asyncio

        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY="test-secret-key-at-least-32-chars-long",
        )
        client = create_redis_client(settings)
        assert isinstance(client, redis.asyncio.Redis)
