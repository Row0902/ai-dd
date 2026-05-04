"""Login user use case.

Handles user authentication and JWT token generation.
"""

from __future__ import annotations

from domain.auth.exceptions import AuthenticationError
from domain.auth.ports import PasswordHasher, TokenService, UserRepository


async def login_user(
    repo: UserRepository,
    hasher: PasswordHasher,
    token_service: TokenService,
    email: str,
    password: str,
) -> dict[str, str]:
    """Authenticate a user and return a JWT token.

    Args:
        repo: User repository port.
        hasher: Password hashing port.
        token_service: Token generation port.
        email: User email address.
        password: Plaintext password to verify.

    Returns:
        Dict with ``access_token`` and ``token_type`` keys.

    Raises:
        AuthenticationError: If credentials are invalid.
    """
    user = await repo.find_by_email(email)
    if user is None or not hasher.verify(password, user.hashed_password):
        raise AuthenticationError("Invalid credentials")
    token = token_service.generate(user.id, user.role.value)
    return {"access_token": token, "token_type": "bearer"}
