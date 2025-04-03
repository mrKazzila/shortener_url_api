import logging

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from validators import url as url_validator
from dishka.integrations.fastapi import FromDishka, DishkaRoute
from app.api.routers.urls._types import PathUrlKey, QueryLongUrl
from app.api.routers.urls.exceptions import (
    InvalidUrlException,
    UrlNotFoundException,
)

from app.service_layer.unit_of_work import UnitOfWork
from app.schemas.urls import SReturnUrl
from app.service_layer.services.urls import UrlsServices

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
    url: str,
    url_service: FromDishka[UrlsServices],
    uow: FromDishka[UnitOfWork],
) -> SReturnUrl:
    """Creates a shortened URL."""
    try:
        if not url_validator(url):
            raise InvalidUrlException()

        return await url_service.create_url(target_url=url, uow=uow)

    except (InvalidUrlException, HTTPException) as error_:
        logger.error(error_)
        raise error_


@router.get(
    path="/{url_key}",
    name="Redirect to long url by key",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def redirect_to_target_url(
    url_key: PathUrlKey,
    request: Request,
    url_service: FromDishka[UrlsServices],
    uow: FromDishka[UnitOfWork],
) -> RedirectResponse:
    """Redirects to the target URL for a given shortened URL key."""
    try:
        if db_url := await url_service.get_active_long_url_by_key(key=url_key, uow=uow):
            await url_service.update_db_clicks(url=db_url, uow=uow)

            return RedirectResponse(
                url=str(db_url.target_url),
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            )

        raise UrlNotFoundException(detail=f"{request.url} doesn't exist!")

    except (UrlNotFoundException, HTTPException) as error_:
        logger.error(error_)
        raise error_
