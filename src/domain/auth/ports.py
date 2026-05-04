"""Auth domain ports: abstract interfaces for infrastructure adapters."""

from abc import ABC, abstractmethod

from domain.auth.entities import Invitation, User


class UserRepository(ABC):
    """Port for user persistence."""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Persist a user and return the saved entity."""

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        """Find a user by email, or None if not found."""

    @abstractmethod
    async def find_by_id(self, user_id: str) -> User | None:
        """Find a user by ID, or None if not found."""


class PasswordHasher(ABC):
    """Port for password hashing and verification."""

    @abstractmethod
    def hash(self, password: str) -> str:
        """Hash a plaintext password."""

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """Verify a plaintext password against a hash."""


class TokenService(ABC):
    """Port for JWT token generation and verification."""

    @abstractmethod
    def generate(self, user_id: str, role: str) -> str:
        """Generate a signed JWT for the given user."""

    @abstractmethod
    def verify(self, token: str) -> dict:
        """Verify a JWT and return its claims dict."""


class InvitationRepository(ABC):
    """Port for invitation persistence."""

    @abstractmethod
    async def save(self, invitation: Invitation) -> Invitation:
        """Persist an invitation and return the saved entity."""

    @abstractmethod
    async def find_by_token(self, token: str) -> Invitation | None:
        """Find an invitation by its UUID4 token, or None."""

    @abstractmethod
    async def mark_as_used(self, token: str) -> bool:
        """Mark an invitation as consumed. Returns True if found and updated."""


class NotificationService(ABC):
    """Port for sending notifications (e.g., invitation emails)."""

    @abstractmethod
    async def send_invitation(
        self, email: str, token: str, inviter_name: str
    ) -> None:
        """Send an invitation notification to the given email."""
