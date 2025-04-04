from http import HTTPStatus

__all__ = (
    "InvalidUrlException",
    "UrlNotFoundException",
    "BaseCustomException",
)


class BaseCustomException(Exception):
    """Base Exception class for custom exceptions."""

    __slots__ = ("status_code", "detail")

    def __init__(self, *, status_code: HTTPStatus | int, detail: str):
        self.status_code = status_code
        self.detail = detail

    def __str__(self) -> str:
        return f"{self.status_code}. {self.detail}"


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
