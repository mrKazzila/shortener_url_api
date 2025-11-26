__all__ = ("MIDDLEWARES",)

from src.presentation.api.middleware.error_middleware import ErrorMiddleware

MIDDLEWARES: tuple = (ErrorMiddleware,)
