"""Tests for infrastructure.persistence.session: async engine and session factory."""

from __future__ import annotations

from sqlalchemy import text

from infrastructure.persistence.session import create_engine_from_url, get_session


class TestCreateEngineFromUrl:
    """Tests for create_engine_from_url() factory."""

    async def test_creates_engine_for_sqlite_memory(self):
        """Should create a working async SQLAlchemy engine for sqlite://."""
        engine = create_engine_from_url("sqlite://")
        assert engine is not None
        # Verify engine can execute a simple query
        async with get_session(engine) as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar_one() == 1
        await engine.dispose()

    async def test_creates_engine_for_sqlite_file(self):
        """Should create engine for sqlite:///path format."""
        engine = create_engine_from_url("sqlite:///./test-temp.db")
        assert engine is not None
        await engine.dispose()
        # Clean up
        import os

        os.remove("./test-temp.db") if os.path.exists("./test-temp.db") else None


class TestGetSession:
    """Tests for get_session() async context manager."""

    async def test_get_session_yields_session(self):
        """get_session should yield a usable AsyncSession."""
        engine = create_engine_from_url("sqlite://")
        async with get_session(engine) as session:
            assert session is not None
            result = await session.execute(text("SELECT 1"))
            assert result.scalar_one() == 1
        await engine.dispose()

    async def test_get_session_creates_tables(self):
        """get_session should create tables when create_all is called."""
        engine = create_engine_from_url("sqlite://")
        # Create tables
        from infrastructure.persistence.session import create_tables

        await create_tables(engine)
        async with get_session(engine) as session:
            # Should be able to query the books table
            result = await session.execute(text("SELECT count(*) FROM books"))
            assert result.scalar_one() == 0
        await engine.dispose()
