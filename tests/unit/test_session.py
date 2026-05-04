"""Tests for infrastructure.persistence.session: engine and session factory."""

from __future__ import annotations

from sqlalchemy import text
from sqlmodel import Session

from infrastructure.persistence.session import create_engine_from_url, get_session


class TestCreateEngineFromUrl:
    """Tests for create_engine_from_url() factory."""

    def test_creates_engine_for_sqlite_memory(self):
        """Should create a working SQLAlchemy engine for sqlite://."""
        engine = create_engine_from_url("sqlite://")
        assert engine is not None
        # Verify engine can execute a simple query
        with Session(engine) as session:
            result = session.exec(text("SELECT 1")).one()
            assert result[0] == 1

    def test_creates_engine_for_sqlite_file(self):
        """Should create engine for sqlite:///path format."""
        engine = create_engine_from_url("sqlite:///./test-temp.db")
        assert engine is not None
        # Clean up
        import os

        os.remove("./test-temp.db") if os.path.exists("./test-temp.db") else None


class TestGetSession:
    """Tests for get_session() context manager."""

    def test_get_session_yields_session(self):
        """get_session should yield a usable SQLModel Session."""
        engine = create_engine_from_url("sqlite://")
        with get_session(engine) as session:
            assert session is not None
            result = session.exec(text("SELECT 1")).one()
            assert result[0] == 1

    def test_get_session_creates_tables(self):
        """get_session should create tables when create_all is called."""
        engine = create_engine_from_url("sqlite://")
        # Create tables
        from sqlmodel import SQLModel

        SQLModel.metadata.create_all(engine)
        with get_session(engine) as session:
            # Should be able to query the books table
            result = session.exec(text("SELECT count(*) FROM books")).one()
            assert result[0] == 0
