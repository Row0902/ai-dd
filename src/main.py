"""FastAPI entrypoint (composition root).

This module preserves the current HTTP contract while delegating business logic
to application use cases and persistence to infrastructure adapters.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.dependencies import get_book_repo
from api.routers.books import router as books_router
from config.settings import AppSettings
from domain.exceptions import AggregatedValidationError, DomainError, ValidationError
from infrastructure.json_book_repository import JsonBookRepository
from infrastructure.memory_book_repository import InMemoryBookRepository
from infrastructure.repository_factory import create_repository
from infrastructure.repository_registry import register


def create_app(settings: AppSettings | None = None) -> FastAPI:
    """Create a FastAPI app wired to a repository adapter.

    Args:
        settings: Application settings. If None, defaults are used with
            ``DATABASE_URL=memory://`` for backward compatibility.

    Returns:
        Configured FastAPI application.
    """
    if settings is None:
        settings = AppSettings(DATABASE_URL="memory://")

    # Register all known repository backends
    register("memory", InMemoryBookRepository)
    register("json", JsonBookRepository)

    repo = create_repository(settings)

    app = FastAPI()
    app.include_router(books_router)
    app.dependency_overrides[get_book_repo] = lambda: repo

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        """Convert domain errors to HTTP 422 with structured detail.

        Registered at the FastAPI **application** level (not router level)
        because FastAPI exception handlers only take effect when added to the
        app instance — router-level ``@router.exception_handler`` does not
        exist in the current API.  Functionally equivalent to the design
        intent.
        """
        if isinstance(exc, AggregatedValidationError):
            detail = [{"field": e.field, "message": e.message} for e in exc.errors]
        elif isinstance(exc, ValidationError):
            detail = [{"field": exc.field, "message": exc.message}]
        else:
            detail = [{"field": "unknown", "message": str(exc)}]
        return JSONResponse(status_code=422, content={"detail": detail})

    @app.get("/")
    def root():
        """Root endpoint."""
        return {"msg": "AI Driven Development - biblioteca digital"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
