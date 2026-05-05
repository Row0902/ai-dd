"""Domain validators: polymorphic validation infrastructure."""

from domain.validators.composite import CompositeValidator
from domain.validators.protocol import Validator

__all__ = ["CompositeValidator", "Validator"]
