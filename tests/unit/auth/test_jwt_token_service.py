"""Unit tests for JwtTokenService."""

import time

import jwt
import pytest

from domain.auth.exceptions import AuthenticationError
from infrastructure.auth.jwt_token_service import JwtTokenService

TEST_SECRET = "test-secret-key-for-jwt-that-is-long-enough"
TEST_SECRET_WRONG = "wrong-secret-key-for-jwt-that-is-long-enough"


class TestJwtTokenServiceGenerate:
    """Test JwtTokenService.generate method."""

    def setup_method(self) -> None:
        """Create a fresh token service for each test."""
        self.service = JwtTokenService(secret_key=TEST_SECRET)

    def test_generate_returns_non_empty_string(self) -> None:
        """Generate returns a non-empty JWT string."""
        token = self.service.generate(user_id="u1", role="user")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_is_valid_jwt(self) -> None:
        """Generate produces a decodable JWT with expected claims."""
        token = self.service.generate(user_id="u1", role="admin")
        claims = jwt.decode(token, TEST_SECRET, algorithms=["HS256"])
        assert claims["sub"] == "u1"
        assert claims["role"] == "admin"
        assert "exp" in claims
        assert "iat" in claims

    def test_generate_different_users_produce_different_tokens(self) -> None:
        """Tokens for different users are different."""
        token1 = self.service.generate(user_id="u1", role="user")
        token2 = self.service.generate(user_id="u2", role="user")
        assert token1 != token2


class TestJwtTokenServiceVerify:
    """Test JwtTokenService.verify method."""

    def setup_method(self) -> None:
        """Create a fresh token service for each test."""
        self.service = JwtTokenService(secret_key=TEST_SECRET)

    def test_verify_returns_correct_claims(self) -> None:
        """Verify returns a dict with correct sub and role claims."""
        token = self.service.generate(user_id="u1", role="admin")
        claims = self.service.verify(token)
        assert claims["sub"] == "u1"
        assert claims["role"] == "admin"

    def test_verify_expired_token_raises_authentication_error(self) -> None:
        """Verify raises AuthenticationError for an expired token."""
        # Create a token that expired 1 hour ago
        payload = {
            "sub": "u1",
            "role": "user",
            "exp": int(time.time()) - 3600,
            "iat": int(time.time()) - 7200,
        }
        token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")
        with pytest.raises(AuthenticationError, match="expired"):
            self.service.verify(token)

    def test_verify_tampered_token_raises_authentication_error(self) -> None:
        """Verify raises AuthenticationError for a token with invalid signature."""
        token = self.service.generate(user_id="u1", role="user")
        # Tamper with the token by changing a character
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        with pytest.raises(AuthenticationError):
            self.service.verify(tampered)

    def test_verify_token_with_wrong_key_raises_authentication_error(self) -> None:
        """Verify raises AuthenticationError when signed with a different key."""
        other_service = JwtTokenService(secret_key=TEST_SECRET_WRONG)
        token = other_service.generate(user_id="u1", role="user")
        with pytest.raises(AuthenticationError):
            self.service.verify(token)

    def test_verify_malformed_token_raises_authentication_error(self) -> None:
        """Verify raises AuthenticationError for a completely malformed string."""
        with pytest.raises(AuthenticationError):
            self.service.verify("not.a.jwt.token.at.all")
