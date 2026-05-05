"""Unit tests for domain exceptions."""

from domain.exceptions import DomainError, ValidationError


class TestDomainError:
    """Test DomainError base exception."""

    def test_domain_error_is_exception(self) -> None:
        """DomainError is a subclass of Exception."""
        assert issubclass(DomainError, Exception)

    def test_domain_error_can_be_raised(self) -> None:
        """DomainError can be raised and caught."""
        try:
            raise DomainError("test error")
        except DomainError as e:
            assert str(e) == "test error"


class TestValidationError:
    """Test ValidationError dataclass."""

    def test_validation_error_is_domain_error(self) -> None:
        """ValidationError is a subclass of DomainError."""
        assert issubclass(ValidationError, DomainError)

    def test_validation_error_has_field_and_message(self) -> None:
        """ValidationError stores field and message attributes."""
        error = ValidationError(field="name", message="Name is required")
        assert error.field == "name"
        assert error.message == "Name is required"

    def test_validation_error_equality(self) -> None:
        """Two ValidationErrors with same field/message are equal."""
        e1 = ValidationError(field="name", message="Name is required")
        e2 = ValidationError(field="name", message="Name is required")
        assert e1 == e2

    def test_validation_error_inequality_different_field(self) -> None:
        """ValidationErrors with different fields are not equal."""
        e1 = ValidationError(field="name", message="Name is required")
        e2 = ValidationError(field="author", message="Name is required")
        assert e1 != e2

    def test_validation_error_inequality_different_message(self) -> None:
        """ValidationErrors with different messages are not equal."""
        e1 = ValidationError(field="name", message="Name is required")
        e2 = ValidationError(field="name", message="Too long")
        assert e1 != e2

    def test_validation_error_is_hashable(self) -> None:
        """ValidationError is hashable (usable in sets and dicts)."""
        error = ValidationError(field="name", message="Name is required")
        assert isinstance(hash(error), int)

    def test_validation_error_hash_equality(self) -> None:
        """Equal ValidationErrors have the same hash."""
        e1 = ValidationError(field="name", message="Name is required")
        e2 = ValidationError(field="name", message="Name is required")
        assert hash(e1) == hash(e2)

    def test_validation_error_can_be_raised_and_caught(self) -> None:
        """ValidationError can be raised and caught as DomainError."""
        try:
            raise ValidationError(field="name", message="required")
        except DomainError as e:
            assert isinstance(e, ValidationError)
            assert e.field == "name"
