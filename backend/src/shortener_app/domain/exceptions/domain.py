__all__ = ("ValidationError",)

from typing import final

from shortener_app.domain.exceptions.base import BaseDomainError


@final
class ValidationError(BaseDomainError):
    """Raised when domain entity validation fails."""
