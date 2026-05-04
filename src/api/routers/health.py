"""Health check router.

Provides a public endpoint for liveness and readiness probes.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    """Return service health status.

    Returns:
        Dict with ``status`` and ``database`` keys.
    """
    return {"status": "ok", "database": "up"}
