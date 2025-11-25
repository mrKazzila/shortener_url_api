from src.infrastructures.exceptions.base import BaseInfraError

__all__ = ("ImproperUoWUsageError",)


class ImproperUoWUsageError(BaseInfraError):
    """Raised when UnitOfWork is used incorrectly."""
