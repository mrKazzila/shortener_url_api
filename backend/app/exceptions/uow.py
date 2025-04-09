from app.exceptions.base import BaseCustomException

__all__ = ("ImproperUoWUsageError",)


class ImproperUoWUsageError(BaseCustomException):
    """Raised when UnitOfWork is used incorrectly."""

    __slots__ = ("detail",)

    def __init__(self, *, detail: str | None = None) -> None:
        default_message = "The session is not initialized. Use UnitOfWork only as a context manager!"
        super().__init__(
            status_code=None,
            detail=detail or default_message,
        )
