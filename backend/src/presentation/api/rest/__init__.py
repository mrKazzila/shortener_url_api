__all__ = ("ROUTERS",)

from src.presentation.api.rest.routers import (
    healthcheck_router,
    urls_router,
    users_router,
)

ROUTERS: tuple = (
    urls_router,
    users_router,
    healthcheck_router,
)
