import logging
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

from app.api.routers.schemas.urls import SReturnUrl, SUserUrl, SUserUrls
from app.api.routers.urls._types import PathUrlKey, QueryLongUrl
from app.dto.urls import UrlDTO, XUserHeader
from app.service_layer.services import UrlsServices

logger = logging.getLogger(__name__)

__all__ = ("router",)


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
    data: FromDishka[XUserHeader],
) -> SReturnUrl:
    """Creates a shortened URL."""
    result = await url_service.create_url(
        url_data=UrlDTO(
            target_url=url,
            user_id=UUID(data),
        ),
    )

    return SReturnUrl(**result.to_dict())


@router.get(
    path="/user_urls",
    name="Get all user urls",
    status_code=status.HTTP_200_OK,
)
async def get_user_urls(
    url_service: FromDishka[UrlsServices],
    data: FromDishka[XUserHeader],
) -> SUserUrls:
    """Get all user urls."""
    user_urls = await url_service.get_user_urls(
        user_id=UUID(data),
        pagination_data={},
    )

    return SUserUrls(
        count=len(user_urls),
        urls=[SUserUrl(**url.to_dict()) for url in user_urls],
    )


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
    return RedirectResponse(
        url=await url_service.update_redirect_counter(key=url_key),
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
