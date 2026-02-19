__all__ = ("MissingUserIdMetadata", "InvalidUserIdMetadata")

from shortener_app.presentation.exceptions.base import BasePresentationError


class MissingUserIdMetadata(BasePresentationError):
    pass


class InvalidUserIdMetadata(BasePresentationError):
    pass
