import logging

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from app.api.routers.urls._types import PathUrlKey, QueryLongUrl
from app.api.routers.urls.exceptions import (
    InvalidUrlException,
    UrlNotFoundException,
)
from app.api.schemas.urls import SReturnUrl
from app.service_layer.services import (
    UrlsServices,
    exceptions as services_exceptions,
)

__all__ = ("router",)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["urls"],
    route_class=DishkaRoute,
)


@router.post(
    path="/",
    name="Create key for short url",
    status_code=status.HTTP_201_CREATED,
)
async def create_short_url(
    url: QueryLongUrl,
    url_service: FromDishka[UrlsServices],
) -> SReturnUrl:
    """Creates a shortened URL."""
    try:
        result = await url_service.create_url(target_url=url)
        return SReturnUrl(
            key=result.key,
            target_url=result.target_url,
        )
    except services_exceptions.InvalidUrlException as error_:
        logger.error(error_)
        raise InvalidUrlException()
    except HTTPException as error_:
        logger.error(error_)
        raise error_


@router.get(
    path="/{url_key}",
    name="Redirect to long url by key",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def redirect_to_target_url(
    url_key: PathUrlKey,
    url_service: FromDishka[UrlsServices],
) -> RedirectResponse:
    """Redirects to the target URL for a given shortened URL key."""
    try:
        redirect_url: str = await url_service.update_redirect_counter_for_url(
            key=url_key,
        )
        return RedirectResponse(
            url=redirect_url,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )
    except services_exceptions.UrlNotFoundException as error_:
        logger.error(error_)
        raise UrlNotFoundException(url_key=url_key)
    except HTTPException as error_:
        logger.error(error_)
        raise error_
