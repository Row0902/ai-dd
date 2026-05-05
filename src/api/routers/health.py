"""Health check router.

Provides a public endpoint for liveness and readiness probes.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from api.dependencies import get_book_repo
from domain.repositories import BookRepository

router = APIRouter()


@router.get("/health")
async def health(
    repo: Annotated[BookRepository, Depends(get_book_repo)],
):
    """Return service health status with a database connectivity probe.

    Performs a lightweight repository operation to verify the persistence
    backend is reachable and responsive.

    Returns:
        HTTP 200 with ``{"status": "ok", "database": "up"}`` when healthy.
        HTTP 503 with ``{"status": "error", "database": "down"}`` when
        the database probe fails.
    """
    try:
        await repo.list(limit=1)
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "down"},
        )
    return {"status": "ok", "database": "up"}
