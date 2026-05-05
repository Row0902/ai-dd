"""SQLAlchemy engine and session factory for database access.

Provides helpers for creating an engine from a ``DATABASE_URL`` string
and obtaining a ``Session`` for use in repository implementations or
as a FastAPI dependency.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlmodel import Session, SQLModel


def create_engine_from_url(database_url: str) -> Engine:
    """Create a SQLAlchemy engine from a database URL.

    Supports ``sqlite://`` (memory), ``sqlite:///path`` (file), and
    ``postgresql://`` connection strings.

    Args:
        database_url: The database connection URL.

    Returns:
        A configured SQLAlchemy Engine instance.
    """
    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, connect_args=connect_args)


def create_tables(engine: Engine) -> None:
    """Create all SQLModel-defined tables in the database.

    Idempotent: existing tables are left unchanged.

    Args:
        engine: The SQLAlchemy engine pointing to the target database.
    """
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session(engine: Engine) -> Generator[Session, None, None]:
    """Yield a SQLModel Session bound to the given engine.

    This is a context manager that commits on success and rolls back
    on exception. Suitable for use as a FastAPI dependency via
    ``functools.partial`` or as a standalone helper.

    Args:
        engine: The SQLAlchemy engine to bind the session to.

    Yields:
        A SQLModel Session instance.
    """
    with Session(engine) as session:
        yield session
