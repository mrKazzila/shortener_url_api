__all__ = (
    "app_setup",
    "create_app",
)

from contextlib import asynccontextmanager

import structlog
from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator

from src.application.interfaces.cache import CacheProtocol
from src.config.settings.base import Settings
from src.config.settings.logging import setup_logging

setup_logging(json_format=False)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app_: FastAPI):
    """Async context manager for app lifespan."""
    logger.info("Service started")
    container: AsyncContainer = app_.state.dishka_container

    cache_service: CacheProtocol = await container.get(CacheProtocol)
    redis_client = getattr(cache_service, "client", None)
    yield

    await redis_client.save()
    await app_.state.dishka_container.close()
    logger.info("Service exited")


def create_app(
    *,
    settings: Settings,
    title: str | None = None,
    description: str | None = None,
    version: str | None = None,
    contact: dict[str, str] | None = None,
) -> FastAPI:
    app_title = title or settings.app_name
    app_description = description
    app_version = version or settings.app_version
    app_contact = contact

    app = FastAPI(
        title=app_title,
        description=app_description,
        version=app_version,
        contact=app_contact,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    tags_metadata = [
        {
            "name": "urls",
            "description": "Urls logic",
        },
        {
            "name": "users",
            "description": "Users url logic",
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
            title=app_title,
            version=app_version,
            description=app_description,
            contact=app_contact,
            routes=app.routes,
            tags=tags_metadata,
        )

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
    return app


def app_setup(
    *,
    app: FastAPI,
    providers: list[Provider],
    middlewares: tuple = (),
    endpoints: tuple[APIRouter] = (),
) -> None:
    try:
        logger.info("Start application setup")

        _setup_prometheus(app=app)

        _di_setup(app=app, providers=providers)
        _routers_setup(app=app, routers=endpoints)
        _middlewares_setup(app=app, middlewares=middlewares)

        logger.info("Application setup successfully done")
    except Exception as error_:
        logger.error(error_)
        exit(error_)


def _di_setup(
    *,
    app: FastAPI,
    providers: list[Provider],
) -> None:
    """Setup project DI."""
    try:
        logger.info("Start DI setup")

        containers = _get_container(providers=providers)
        setup_dishka(app=app, container=containers)

        logger.info("Add containers to APP state")
        app.state.dishka_container = containers

        logger.info("DI setup successfully done")
    except Exception as error_:
        logger.error(error_)
        exit(error_)


def _get_container(*, providers: list[Provider]) -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        *providers,
    )


def _routers_setup(
    *,
    app: FastAPI,
    routers: tuple[APIRouter],
) -> None:
    """Setup project routers."""
    try:
        logger.info("Start routers setup")

        [app.include_router(router) for router in routers]

        logger.info("Routers setup successfully done")
    except Exception as error_:
        logger.error(error_)
        exit(error_)


def _middlewares_setup(
    *,
    app: FastAPI,
    middlewares: tuple,
) -> None:
    """Setup project middlewares."""
    try:
        logger.info("Start middlewares setup")

        [app.add_middleware(middleware) for middleware in middlewares]

        logger.info("Middlewares setup successfully done")
    except Exception as error_:
        logger.error(error_)
        exit(error_)


def _setup_prometheus(app: FastAPI):
    try:
        logger.info("Setting up Prometheus metrics")

        instrumentator = Instrumentator(
            should_group_status_codes=False,
            should_ignore_untemplated=False,
            should_respect_env_var=False,
            excluded_handlers=["/metrics"],
            inprogress_name="http_requests_inprogress",
            inprogress_labels=True,
        )

        instrumentator.instrument(app).expose(
            app,
            endpoint="/metrics",
            include_in_schema=False,
        )

        logger.info("Prometheus metrics setup completed")

    except Exception as e:
        logger.error(f"Failed to setup Prometheus: {e}")
        raise
