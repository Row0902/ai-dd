"""Redis client factory for rate limiting."""

from __future__ import annotations

import redis.asyncio

from config.settings import AppSettings


def create_redis_client(settings: AppSettings) -> redis.asyncio.Redis:
    """Create an async Redis client from application settings.

    Args:
        settings: Application settings containing ``REDIS_URL``.

    Returns:
        A connected ``redis.asyncio.Redis`` client.
    """
    return redis.asyncio.Redis.from_url(settings.REDIS_URL)
