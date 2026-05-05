"""Tests for T1: redis dependency is importable."""


def test_redis_is_importable():
    """Verify redis package is installed and importable."""
    import redis

    assert redis.__version__


def test_redis_asyncio_is_importable():
    """Verify redis.asyncio (async client) is available."""
    import redis.asyncio

    assert hasattr(redis.asyncio, "Redis")
