from typing import final

from src.domain.exceptions.base import BaseDomainError


@final
class ValidationError(BaseDomainError):
    """Raised when domain entity validation fails."""
