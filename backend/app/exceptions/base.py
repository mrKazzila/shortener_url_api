from http import HTTPStatus

__all__ = ("BaseCustomException",)


class BaseCustomException(Exception):
    """Base Exception class for custom exceptions."""

    __slots__ = ("status_code", "detail")

    def __init__(
        self,
        *,
        status_code: HTTPStatus | int | None = None,
        detail: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.detail = detail

    def __repr__(self) -> str:
        return f"{self.status_code}. {self.detail}"
