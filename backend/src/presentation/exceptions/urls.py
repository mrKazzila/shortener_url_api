from http import HTTPStatus

from src.presentation.exceptions.base import BasePresentationError

__all__ = ("UrlNotFoundException",)


class UrlNotFoundException(BasePresentationError):
    def __init__(
        self,
        *,
        status_code: HTTPStatus | int = HTTPStatus.NOT_FOUND,
        url_key: str,
    ) -> None:
        self.status_code = status_code
        self.detail = f"URL with {url_key} key doesn't exist!"

    def __str__(self) -> str:
        return f"{self.status_code}. {self.detail}. "
