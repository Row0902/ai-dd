"""In-memory user repository for testing and development."""

from __future__ import annotations

from domain.auth.entities import User
from domain.auth.ports import UserRepository


class InMemoryUserRepository(UserRepository):
    """Dict-backed user repository.

    Intended for testing and development. Replaced by SQLUserRepository
    when session management is wired.
    """

    def __init__(self) -> None:
        """Initialize with an empty store."""
        self._users: dict[str, User] = {}
        self._by_email: dict[str, str] = {}

    async def save(self, user: User) -> User:
        """Persist a user and return the saved entity.

        Args:
            user: User entity to save.

        Returns:
            The saved user.
        """
        self._users[user.id] = user
        self._by_email[user.email] = user.id
        return user

    async def find_by_email(self, email: str) -> User | None:
        """Find a user by email, or None if not found.

        Args:
            email: Email address to search for.

        Returns:
            User if found, None otherwise.
        """
        user_id = self._by_email.get(email)
        if user_id is None:
            return None
        return self._users.get(user_id)

    async def find_by_id(self, user_id: str) -> User | None:
        """Find a user by ID, or None if not found.

        Args:
            user_id: User ID to search for.

        Returns:
            User if found, None otherwise.
        """
        return self._users.get(user_id)
