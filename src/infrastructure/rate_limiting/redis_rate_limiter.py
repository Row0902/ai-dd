"""Redis-backed rate limiter using sorted sets for sliding window counting."""

from __future__ import annotations

import time

import structlog

from domain.rate_limiting.ports import RateLimiter

logger = structlog.get_logger(__name__)


class RedisRateLimiter(RateLimiter):
    """Sliding window rate limiter backed by Redis Sorted Sets.

    Uses an atomic pipeline: ZREMRANGEBYSCORE → ZCARD → ZADD → EXPIRE.
    Fail-open on Redis errors: returns True and logs a warning.
    """

    def __init__(self, redis_client) -> None:
        """Initialize with an async Redis client.

        Args:
            redis_client: A ``redis.asyncio.Redis`` (or compatible) instance.
        """
        self._redis = redis_client

    async def check(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if a request is allowed using a sliding window.

        Args:
            key: Unique identifier for the rate limit scope.
            max_requests: Maximum requests allowed in the window.
            window_seconds: Duration of the sliding window in seconds.

        Returns:
            True if allowed, False if limit exceeded. Fail-open on errors.
        """
        try:
            now = time.time()
            window_start = now - window_seconds

            pipe = self._redis.pipeline(transaction=True)
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {f"{now}": now})
            pipe.expire(key, window_seconds)
            results = await pipe.execute()

            current_count = results[1]
            if current_count >= max_requests:
                # Remove the entry we just added — it was over the limit
                await self._redis.zrem(key, f"{now}")
                return False
            return True
        except Exception:
            logger.warning(
                "rate_limiter_unavailable",
                message="Rate limiter unavailable, allowing request",
                key=key,
            )
            return True

    async def reset(self, key: str) -> None:
        """Reset the rate limit counter for a given key.

        Args:
            key: The rate limit key to reset.
        """
        try:
            await self._redis.delete(key)
        except Exception:
            logger.warning(
                "rate_limiter_reset_failed",
                message="Failed to reset rate limiter key",
                key=key,
            )
