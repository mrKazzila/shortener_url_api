from src.presentation.api.rest.routers import (
    healthcheck_router,
    urls_router,
    users_router,
)

ROUTERS: tuple = (urls_router, users_router, healthcheck_router)

__all__ = ("ROUTERS",)
