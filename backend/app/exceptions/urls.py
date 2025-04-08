from http import HTTPStatus

from app.exceptions.base import BaseCustomException

__all__ = (
    "InvalidUrlException",
    "UrlNotFoundException",
)


class InvalidUrlException(BaseCustomException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid url!",
        )


class UrlNotFoundException(BaseCustomException):
    __slots__ = ("url_key",)

    def __init__(self, *, url_key: str) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"URL with {url_key} key doesn't exist!",
        )
