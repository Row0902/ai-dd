"""Infrastructure rate limiting package: adapters for domain rate limiter port."""

from __future__ import annotations

from infrastructure.rate_limiting.noop_rate_limiter import NoOpRateLimiter

__all__ = ["NoOpRateLimiter"]
