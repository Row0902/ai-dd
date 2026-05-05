"""Register user use case.

Handles user registration with duplicate-email detection and password hashing.
"""

from __future__ import annotations

import uuid

from domain.auth.entities import User, UserRole
from domain.auth.exceptions import UserAlreadyExists
from domain.auth.ports import PasswordHasher, UserRepository


async def register_user(
    repo: UserRepository,
    hasher: PasswordHasher,
    email: str,
    password: str,
    role: UserRole = UserRole.USER,
) -> User:
    """Register a new user.

    Args:
        repo: User repository port.
        hasher: Password hashing port.
        email: User email address.
        password: Plaintext password (will be hashed).
        role: User role (default USER).

    Returns:
        The persisted User entity.

    Raises:
        UserAlreadyExists: If a user with the given email already exists.
    """
    existing = await repo.find_by_email(email)
    if existing:
        raise UserAlreadyExists(f"Email already registered: {email}")
    user = User(
        id=uuid.uuid4().hex,
        email=email,
        hashed_password=hasher.hash(password),
        role=role,
    )
    return await repo.save(user)
