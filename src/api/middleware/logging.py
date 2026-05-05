"""structlog request/response logging middleware for FastAPI."""

from __future__ import annotations

import time
import uuid

import structlog
from fastapi import Request


async def logging_middleware(request: Request, call_next):
    """Log every request with structlog.

    Attaches a unique ``request_id`` to ``Request.state`` and the
    ``X-Request-ID`` response header.  Reads ``user_id`` from
    ``request.state`` when an auth dependency has populated it.

    Args:
        request: The incoming HTTP request.
        call_next: The next middleware/endpoint in the chain.

    Returns:
        The HTTP response with added headers.
    """
    logger = structlog.get_logger()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.monotonic()

    response = await call_next(request)

    duration_ms = (time.monotonic() - start) * 1000
    log_data: dict = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(duration_ms, 2),
    }
    if hasattr(request.state, "user_id"):
        log_data["user_id"] = request.state.user_id
    logger.info("request", **log_data)
    response.headers["X-Request-ID"] = request_id
    return response
