"""Unit tests for BcryptPasswordHasher."""

from infrastructure.auth.bcrypt_password_hasher import BcryptPasswordHasher


class TestBcryptPasswordHasher:
    """Test BcryptPasswordHasher implements PasswordHasher correctly."""

    def setup_method(self) -> None:
        """Create a fresh hasher for each test."""
        self.hasher = BcryptPasswordHasher()

    def test_hash_returns_non_empty_string(self) -> None:
        """Hash returns a non-empty string."""
        result = self.hasher.hash("password123")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_returns_different_string_than_input(self) -> None:
        """Hash output is not the same as the input password."""
        result = self.hasher.hash("password123")
        assert result != "password123"

    def test_hash_is_deterministic_different_hashes(self) -> None:
        """Hashing the same password twice produces different hashes (different salts)."""
        hash1 = self.hasher.hash("password123")
        hash2 = self.hasher.hash("password123")
        assert hash1 != hash2

    def test_verify_correct_password_returns_true(self) -> None:
        """Verify returns True when password matches the hash."""
        hashed = self.hasher.hash("password123")
        assert self.hasher.verify("password123", hashed) is True

    def test_verify_wrong_password_returns_false(self) -> None:
        """Verify returns False when password does not match the hash."""
        hashed = self.hasher.hash("password123")
        assert self.hasher.verify("wrongpassword", hashed) is False

    def test_verify_empty_password_against_hash(self) -> None:
        """Verify returns False for empty password against a non-empty hash."""
        hashed = self.hasher.hash("password123")
        assert self.hasher.verify("", hashed) is False

    def test_hash_empty_password(self) -> None:
        """Hashing an empty password still produces a valid hash."""
        hashed = self.hasher.hash("")
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert self.hasher.verify("", hashed) is True

    def test_hash_unicode_password(self) -> None:
        """Hashing a unicode password works correctly."""
        password = "pässwördÜñîçødé"
        hashed = self.hasher.hash(password)
        assert self.hasher.verify(password, hashed) is True
        assert self.hasher.verify("wrong", hashed) is False

    def test_hash_uses_bcrypt_prefix(self) -> None:
        """Hash output starts with bcrypt identifier prefix."""
        hashed = self.hasher.hash("test")
        assert hashed.startswith("$2b$")
