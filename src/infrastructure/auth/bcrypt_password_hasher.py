"""Bcrypt-based password hasher implementing the PasswordHasher port."""

import bcrypt

from domain.auth.ports import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    """Password hasher using bcrypt with configurable work factor.

    Attributes:
        rounds: bcrypt cost factor (default 12).
    """

    def __init__(self, rounds: int = 12) -> None:
        """Initialize with the given bcrypt rounds.

        Args:
            rounds: bcrypt cost factor.
        """
        self.rounds = rounds

    def hash(self, password: str) -> str:
        """Hash a plaintext password using bcrypt.

        Args:
            password: Plaintext password to hash.

        Returns:
            Bcrypt-hashed password string.
        """
        return bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt(rounds=self.rounds)
        ).decode("utf-8")

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a plaintext password against a bcrypt hash.

        Args:
            password: Plaintext password to verify.
            hashed: Bcrypt hash to verify against.

        Returns:
            True if the password matches, False otherwise.
        """
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
