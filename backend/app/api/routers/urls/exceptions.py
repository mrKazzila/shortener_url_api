from fastapi import HTTPException, status

__all__ = (
    "InvalidUrlException",
    "UrlNotFoundException",
)


class BaseUrlException(HTTPException):
    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}: "
            f"status_code={self.status_code}, "
            f"info={self.detail}"
        )


class InvalidUrlException(BaseUrlException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid url!",
        )


class UrlNotFoundException(BaseUrlException):
    def __init__(self, *, url_key: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"URL with {url_key} key doesn't exist!",
        )
