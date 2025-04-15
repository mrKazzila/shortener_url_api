import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.settings.config import settings

__all__ = (
    "create_app",
    "routers_setup",
    "middlewares_setup",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_: FastAPI):
    logger.info("Service started")

    yield
    await app_.state.dishka_container.close()

    logger.info("Service exited")


def create_app(
    *,
    title: str,
    description: str,
    version: str,
    contact: dict[str, str],
) -> FastAPI:
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        contact=contact,
        lifespan=lifespan,
    )

    tags_metadata = [
        {
            "name": "urls",
            "description": "Urls logic",
        },
        {
            "name": "healthcheck",
            "description": "For ping",
        },
    ]

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=title,
            version=version,
            description=description,
            contact=contact,
            routes=app.routes,
            tags=tags_metadata,
        )

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
    return app


def routers_setup(*, app: FastAPI, endpoints: list[APIRouter]) -> None:
    """Setup project routers."""
    try:
        logger.info("Start routers setup")

        [app.include_router(endpoint) for endpoint in endpoints]

        logger.info("Routers setup successfully done")
    except Exception as error_:
        logger.error(error_)
        exit(error_)


def middlewares_setup(*, app: FastAPI, middlewares: list) -> None:
    """Setup project middlewares."""
    try:
        logger.info("Start middlewares setup")

        [app.add_middleware(middleware) for middleware in middlewares]

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BASE_URL,
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=[
                "Content-Type",
                "Access-Control-Allow-Origin",
            ],
        )

        logger.info("Middlewares setup successfully done")
    except Exception as error_:
        logger.error(error_)
        exit(error_)
