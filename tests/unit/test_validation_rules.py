"""Tests for domain.validation_rules: single source of truth for constraints."""

from domain.validation_rules import (
    ISBN_PATTERN,
    MAX_AUTHOR_LENGTH,
    MAX_TITLE_LENGTH,
    MAX_URL_LENGTH,
    MIN_PUBLICATION_YEAR,
    RULES_VERSION,
)


class TestValidationRulesExist:
    """Verify all validation rule constants are defined and have correct types."""

    def test_max_title_length_is_int(self):
        """MAX_TITLE_LENGTH must be a positive integer."""
        assert isinstance(MAX_TITLE_LENGTH, int)
        assert MAX_TITLE_LENGTH > 0

    def test_max_author_length_is_int(self):
        """MAX_AUTHOR_LENGTH must be a positive integer."""
        assert isinstance(MAX_AUTHOR_LENGTH, int)
        assert MAX_AUTHOR_LENGTH > 0

    def test_min_publication_year_is_int(self):
        """MIN_PUBLICATION_YEAR must be a positive integer."""
        assert isinstance(MIN_PUBLICATION_YEAR, int)
        assert MIN_PUBLICATION_YEAR > 0

    def test_max_url_length_is_int(self):
        """MAX_URL_LENGTH must be a positive integer."""
        assert isinstance(MAX_URL_LENGTH, int)
        assert MAX_URL_LENGTH > 0

    def test_isbn_pattern_is_string(self):
        """ISBN_PATTERN must be a non-empty string (regex pattern)."""
        assert isinstance(ISBN_PATTERN, str)
        assert len(ISBN_PATTERN) > 0

    def test_rules_version_is_string(self):
        """RULES_VERSION must be a non-empty string."""
        assert isinstance(RULES_VERSION, str)
        assert len(RULES_VERSION) > 0


class TestValidationRulesValues:
    """Verify constants match the expected values from spec and existing code."""

    def test_max_title_length_value(self):
        """Title max length must be 200 (matches existing BookName)."""
        assert MAX_TITLE_LENGTH == 200

    def test_max_author_length_value(self):
        """Author max length must be 150 (matches existing BookAuthor)."""
        assert MAX_AUTHOR_LENGTH == 150

    def test_min_publication_year_value(self):
        """Min publication year must be 1000."""
        assert MIN_PUBLICATION_YEAR == 1000

    def test_max_url_length_value(self):
        """URL max length must be 2048 (matches existing BookUrl)."""
        assert MAX_URL_LENGTH == 2048

    def test_rules_version_value(self):
        """Rules version must start at 1.0."""
        assert RULES_VERSION == "1.0"
