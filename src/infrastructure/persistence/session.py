"""Async SQLAlchemy engine and session factory for database access.

Provides helpers for creating an async engine from a ``DATABASE_URL`` string
and obtaining an ``AsyncSession`` for use in repository implementations or
as a FastAPI dependency.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlmodel import SQLModel


def _normalize_async_url(database_url: str) -> str:
    """Convert a sync database URL to its async equivalent.

    Handles:
    - ``sqlite://`` → ``sqlite+aiosqlite://``
    - ``sqlite:///path`` → ``sqlite+aiosqlite:///path``
    - ``postgresql://`` → ``postgresql+asyncpg://``

    URLs already using an async driver are returned unchanged.

    Args:
        database_url: The database connection URL.

    Returns:
        URL string with async driver prefix.
    """
    if database_url.startswith("sqlite://"):
        return database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if database_url.startswith("sqlite:///"):
        return database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url


def create_engine_from_url(database_url: str) -> AsyncEngine:
    """Create an async SQLAlchemy engine from a database URL.

    Supports ``sqlite://`` (memory), ``sqlite:///path`` (file), and
    ``postgresql://`` connection strings. Sync URLs are automatically
    converted to their async equivalents.

    Args:
        database_url: The database connection URL.

    Returns:
        A configured async SQLAlchemy Engine instance.
    """
    async_url = _normalize_async_url(database_url)
    connect_args: dict[str, object] = {}
    if async_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_async_engine(async_url, connect_args=connect_args)


async def create_tables(engine: AsyncEngine) -> None:
    """Create all SQLModel-defined tables in the database.

    Idempotent: existing tables are left unchanged.

    Args:
        engine: The async SQLAlchemy engine pointing to the target database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def get_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    """Yield an AsyncSession bound to the given engine.

    This is an async context manager that commits on success and rolls back
    on exception. Suitable for use as a FastAPI dependency or as a standalone
    helper.

    Args:
        engine: The async SQLAlchemy engine to bind the session to.

    Yields:
        An AsyncSession instance.
    """
    async with AsyncSession(engine) as session:
        yield session
