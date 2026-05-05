"""FastAPI entrypoint (composition root).

This module preserves the current HTTP contract while delegating business logic
to application use cases and persistence to infrastructure adapters.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from urllib.parse import urlparse

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.dependencies import get_book_repo, get_settings
from api.middleware.logging import logging_middleware
from api.routers.auth import router as auth_router
from api.routers.books import router as books_router
from api.routers.collections import router as collections_router
from api.routers.favorites import router as favorites_router
from api.routers.health import router as health_router
from config.settings import AppSettings
from domain.auth.exceptions import (
    AuthenticationError,
    AuthorizationError,
    UserAlreadyExists,
)
from domain.exceptions import AggregatedValidationError, DomainError, ValidationError
from domain.rate_limiting.exceptions import RateLimitExceededError
from infrastructure.json_book_repository import JsonBookRepository
from infrastructure.memory_book_repository import InMemoryBookRepository
from infrastructure.repository_factory import create_repository
from infrastructure.repository_registry import register

logger = structlog.get_logger(__name__)

# ── SQL backend (lazy-initialised per app instance) ────────────────
_sql_engine = None


async def _sql_repo_dependency():
    """FastAPI dependency: yield a fresh SQLBookRepository per request.

    Only active when ``DATABASE_URL`` uses a SQL scheme
    (``sqlite://`` or ``postgresql://``).  The engine is created once
    in ``create_app()`` and the session is scoped to the request.
    """
    from sqlalchemy.ext.asyncio import AsyncSession

    from infrastructure.persistence.sql_book_repository import SQLBookRepository

    async with AsyncSession(_sql_engine) as session:
        yield SQLBookRepository(session)


# ── Lifespan ──────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events.

    On startup: logs readiness and creates database tables when a SQL
    engine is available.
    On shutdown: disposes the SQL engine and logs graceful termination.

    Args:
        app: The FastAPI application instance.
    """
    logger.info("startup", action="starting", service="ai-dd")
    engine = getattr(app.state, "db_engine", None)
    if engine is not None:
        from infrastructure.persistence.session import create_tables

        await create_tables(engine)
        logger.info("startup", action="tables_created")
    yield
    if engine is not None:
        await engine.dispose()
        logger.info("shutdown", action="engine_disposed")
    logger.info("shutdown", action="stopping", service="ai-dd")


# ── Application factory ───────────────────────────────────────────


def create_app(settings: AppSettings | None = None) -> FastAPI:
    """Create a FastAPI app wired to a repository adapter.

    Backend resolution (by ``DATABASE_URL`` scheme):

    * ``memory://`` — ``InMemoryBookRepository`` (tests / dev default)
    * ``json://``   — ``JsonBookRepository`` (legacy file persistence)
    * ``sqlite://`` — ``SQLBookRepository`` with aiosqlite
    * ``postgresql://`` — ``SQLBookRepository`` with asyncpg

    Args:
        settings: Application settings. If None, defaults are used with
            ``DATABASE_URL=memory://`` for backward compatibility.

    Returns:
        Configured FastAPI application.
    """
    global _sql_engine

    if settings is None:
        settings = AppSettings(DATABASE_URL="memory://")

    scheme = urlparse(settings.DATABASE_URL).scheme or "memory"

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

    # ── Repository wiring ─────────────────────────────────────
    if scheme in ("sqlite", "postgresql"):
        # SQL backend: create engine → per-request session dependency
        from infrastructure.persistence.session import create_engine_from_url

        _sql_engine = create_engine_from_url(settings.DATABASE_URL)
        repo_dep = _sql_repo_dependency
    else:
        # In-memory / file backend: singleton repo instance
        register("memory", InMemoryBookRepository)
        register("json", JsonBookRepository)
        repo = create_repository(settings)

        def repo_dep():
            return repo

    app = FastAPI(lifespan=lifespan)
    app.state.db_engine = _sql_engine if scheme in ("sqlite", "postgresql") else None

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
    app.include_router(collections_router)
    app.include_router(favorites_router)

    # Dependency overrides
    app.dependency_overrides[get_book_repo] = repo_dep
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
        logger.error(
            "domain_error",
            exception_type=type(exc).__name__,
            message=str(exc),
            path=request.url.path,
            exc_info=True,
        )
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
        logger.warning(
            "authentication_error",
            exception_type=type(exc).__name__,
            message=str(exc),
            path=request.url.path,
        )
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(AuthorizationError)
    async def authorization_error_handler(
        request: Request, exc: AuthorizationError
    ) -> JSONResponse:
        """Convert AuthorizationError to HTTP 403."""
        logger.warning(
            "authorization_error",
            exception_type=type(exc).__name__,
            message=str(exc),
            path=request.url.path,
        )
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(UserAlreadyExists)
    async def user_already_exists_handler(
        request: Request, exc: UserAlreadyExists
    ) -> JSONResponse:
        """Convert UserAlreadyExists to HTTP 409."""
        logger.warning(
            "user_already_exists",
            exception_type=type(exc).__name__,
            message=str(exc),
            path=request.url.path,
        )
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(RateLimitExceededError)
    async def rate_limit_handler(
        request: Request, exc: RateLimitExceededError
    ) -> JSONResponse:
        """Convert RateLimitExceededError to HTTP 429."""
        logger.warning(
            "rate_limit_exceeded",
            exception_type=type(exc).__name__,
            message=str(exc),
            path=request.url.path,
            retry_after=exc.retry_after,
        )
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"},
            headers={"Retry-After": str(exc.retry_after)},
        )

    @app.get("/")
    def root():
        """Root endpoint."""
        return {"msg": "AI Driven Development - biblioteca digital"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
