__all__ = ("ImproperUoWUsageError",)


class UnitOfWorkError(Exception):
    """Base exception for all UoW-related errors."""


class ImproperUoWUsageError(UnitOfWorkError):
    """Raised when UnitOfWork is used incorrectly."""

    def __init__(self, message: str | None = None) -> None:
        default_message = "The session is not initialized. Use UnitOfWork only as a context manager!"
        super().__init__(message or default_message)
