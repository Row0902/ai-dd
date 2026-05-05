"""SQL-backed user repository implementation.

Implements the ``UserRepository`` port using async SQLAlchemy sessions.
Domain ``User`` entities are converted to/from ``UserModel`` inline.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.auth.entities import User, UserRole
from domain.auth.ports import UserRepository
from infrastructure.auth.sql_models import UserModel


class SQLUserRepository(UserRepository):
    """UserRepository backed by a SQL database via async SQLAlchemy.

    The session is injected via constructor for testability and
    per-request scoping.

    Args:
        session: An AsyncSession instance.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with an async database session.

        Args:
            session: Active async SQLAlchemy session for database operations.
        """
        self._session = session

    async def save(self, user: User) -> User:
        """Persist a user and return the saved entity.

        Args:
            user: Domain User entity to persist.

        Returns:
            The persisted User entity.
        """
        model = UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_domain(model)

    async def find_by_email(self, email: str) -> User | None:
        """Find a user by email address.

        Args:
            email: Email address to search for.

        Returns:
            User if found, None otherwise.
        """
        stmt = select(UserModel).where(UserModel.email == email)  # ty: ignore[invalid-argument-type]
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return _to_domain(model)

    async def find_by_id(self, user_id: str) -> User | None:
        """Find a user by ID.

        Args:
            user_id: Unique identifier of the user.

        Returns:
            User if found, None otherwise.
        """
        model = await self._session.get(UserModel, user_id)
        if model is None:
            return None
        return _to_domain(model)


def _to_domain(model: UserModel) -> User:
    """Convert a UserModel to a domain User entity.

    Args:
        model: The SQLModel database row.

    Returns:
        Domain User entity.
    """
    return User(
        id=model.id,
        email=model.email,
        hashed_password=model.hashed_password,
        role=UserRole(model.role),
        is_active=model.is_active,
        created_at=model.created_at,
    )
