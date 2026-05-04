"""JWT-based token service implementing the TokenService port."""

import time
from typing import Any

import jwt

from domain.auth.exceptions import AuthenticationError
from domain.auth.ports import TokenService

DEFAULT_EXPIRE_MINUTES = 30


class JwtTokenService(TokenService):
    """Token service using PyJWT with HS256 signing.

    Attributes:
        secret_key: HMAC signing key.
        algorithm: JWT algorithm (default HS256).
        expire_minutes: Token lifetime in minutes.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        expire_minutes: int = DEFAULT_EXPIRE_MINUTES,
    ) -> None:
        """Initialize with signing configuration.

        Args:
            secret_key: HMAC secret for signing tokens.
            algorithm: JWT signing algorithm.
            expire_minutes: Token lifetime in minutes.
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def generate(self, user_id: str, role: str) -> str:
        """Generate a signed JWT for the given user.

        Args:
            user_id: The user's unique identifier.
            role: The user's role string.

        Returns:
            Encoded JWT string.
        """
        now = int(time.time())
        payload: dict[str, Any] = {
            "sub": user_id,
            "role": role,
            "iat": now,
            "exp": now + (self.expire_minutes * 60),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify(self, token: str) -> dict:
        """Verify a JWT and return its claims.

        Args:
            token: Encoded JWT string.

        Returns:
            Decoded claims dict with 'sub', 'role', 'exp', 'iat'.

        Raises:
            AuthenticationError: If token is expired, invalid, or tampered.
        """
        try:
            return jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationError("token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise AuthenticationError("invalid token") from exc
