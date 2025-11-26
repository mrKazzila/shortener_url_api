__all__ = (
    "healthcheck_router",
    "urls_router",
    "users_router",
)

from src.presentation.api.rest.routers.healthcheck import (
    router as healthcheck_router,
)
from src.presentation.api.rest.routers.urls import router as urls_router
from src.presentation.api.rest.routers.users import router as users_router
