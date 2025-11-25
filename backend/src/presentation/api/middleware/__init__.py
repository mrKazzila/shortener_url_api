from src.presentation.api.middleware.error_middleware import ErrorMiddleware

MIDDLEWARES: tuple = (ErrorMiddleware,)

__all__ = ("MIDDLEWARES",)
