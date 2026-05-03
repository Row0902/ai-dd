"""FastAPI entrypoint (composition root).

This module preserves the current HTTP contract while delegating business logic
to application use cases and persistence to infrastructure adapters.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.dependencies import get_book_repo
from api.routers.books import router as books_router
from domain.exceptions import AggregatedValidationError, DomainError, ValidationError
from infrastructure.json_book_repository import JsonBookRepository

DATA_FILE = Path(__file__).parent / "library.json"


def create_app(data_file: Path = DATA_FILE) -> FastAPI:
    """Create a FastAPI app wired to a JSON repository adapter."""
    repo = JsonBookRepository(data_file)

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
