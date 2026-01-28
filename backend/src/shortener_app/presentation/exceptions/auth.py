__all__ = ("UserHeaderNotFoundException",)

from http import HTTPStatus

from shortener_app.presentation.exceptions.base import BasePresentationError


class UserHeaderNotFoundException(BasePresentationError):
    """Raised when the request does not contain a custom header."""

    def __init__(
        self,
        *,
        status_code: HTTPStatus | int = HTTPStatus.UNAUTHORIZED,
    ) -> None:
        self.status_code = status_code
        self.detail = "User ID required"

    def __str__(self) -> str:
        return f"{self.status_code}. {self.detail}."
