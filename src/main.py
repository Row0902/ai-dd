"""FastAPI entrypoint (composition root).

This module preserves the current HTTP contract while delegating business logic
to application use cases and persistence to infrastructure adapters.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.dependencies import get_book_repo, get_settings
from api.middleware.logging import logging_middleware
from api.routers.auth import router as auth_router
from api.routers.books import router as books_router
from api.routers.health import router as health_router
from config.settings import AppSettings
from domain.auth.exceptions import (
    AuthenticationError,
    AuthorizationError,
    UserAlreadyExists,
)
from domain.exceptions import AggregatedValidationError, DomainError, ValidationError
from infrastructure.json_book_repository import JsonBookRepository
from infrastructure.memory_book_repository import InMemoryBookRepository
from infrastructure.repository_factory import create_repository
from infrastructure.repository_registry import register

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events.

    On startup: logs that the service is ready.
    On shutdown: drains in-flight requests and logs graceful termination.

    Args:
        app: The FastAPI application instance.
    """
    logger.info("startup", event="starting", service="ai-dd")
    yield
    logger.info("shutdown", event="stopping", service="ai-dd")


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

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
            if settings.ENV == "production"
            else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Register all known repository backends
    register("memory", InMemoryBookRepository)
    register("json", JsonBookRepository)

    repo = create_repository(settings)

    app = FastAPI(lifespan=lifespan)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Logging middleware
    app.middleware("http")(logging_middleware)

    # Routers
    app.include_router(books_router)
    app.include_router(auth_router)
    app.include_router(health_router)

    # Dependency overrides
    app.dependency_overrides[get_book_repo] = lambda: repo
    app.dependency_overrides[get_settings] = lambda: settings

    # Exception handlers
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

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(
        request: Request, exc: AuthenticationError
    ) -> JSONResponse:
        """Convert AuthenticationError to HTTP 401."""
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(AuthorizationError)
    async def authorization_error_handler(
        request: Request, exc: AuthorizationError
    ) -> JSONResponse:
        """Convert AuthorizationError to HTTP 403."""
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(UserAlreadyExists)
    async def user_already_exists_handler(
        request: Request, exc: UserAlreadyExists
    ) -> JSONResponse:
        """Convert UserAlreadyExists to HTTP 409."""
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.get("/")
    def root():
        """Root endpoint."""
        return {"msg": "AI Driven Development - biblioteca digital"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
