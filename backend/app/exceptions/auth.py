from http import HTTPStatus

from app.exceptions.base import BaseCustomException

__all__ = ("UserHeaderNotFoundException",)


class UserHeaderNotFoundException(BaseCustomException):
    """Raised when the request does not contain a custom header."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User ID required",
        )
