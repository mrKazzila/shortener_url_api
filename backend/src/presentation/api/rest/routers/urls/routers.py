__all__ = ("router",)

from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

from src.application.dtos.urls import CreateUrlDTO
from src.application.dtos.users import XUserHeaderDTO  # noqa
from src.application.use_cases import (
    CreateUrlUseCase,
    RedirectToOriginalUrlUseCase,
)
from src.presentation.api.rest.routers.urls._types import (
    PathUrlKey,
    QueryLongUrl,
)
from src.presentation.api.schemas.urls import SUrlResponse
from src.presentation.exceptions.urls import UrlNotFoundException
from src.presentation.mappers.url_mapper import UrlPresentationMapper

router: APIRouter = APIRouter(
    prefix="/urls",
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
    # header: FromDishka[XUserHeaderDTO],
    use_case: FromDishka[CreateUrlUseCase],
    mapper: FromDishka[UrlPresentationMapper],
) -> SUrlResponse:
    """Creates a shortened URL."""
    created_dto = await use_case.execute(
        dto=CreateUrlDTO(
            target_url=url,
            # user_id=UUID(header.x_user_id),
            user_id=UUID("3b0e3fe7-e753-4e14-9ff4-0a200c2cbdcf"),
        ),
    )

    return mapper.to_response(dto=created_dto)


@router.get(
    path="/{url_key}",
    name="Redirect to long url by key",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def redirect_to_target_url(
    url_key: PathUrlKey,
    use_case: FromDishka[RedirectToOriginalUrlUseCase],
) -> RedirectResponse:
    """Redirects to the target URL for a given shortened URL key."""
    if target_url := await use_case.execute(key=url_key):
        return RedirectResponse(
            url=target_url,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    raise UrlNotFoundException(url_key=url_key)


@router.patch(
    path="/{url_key}",
    name="Update url information",
    status_code=status.HTTP_201_CREATED,
)
async def update_url(
    url: QueryLongUrl,
    # header: FromDishka[XUserHeaderDTO],
    # use_case: FromDishka[CreateUrlUseCase],
    # mapper: FromDishka[UrlPresentationMapper],
) -> SUrlResponse:
    """Creates a shortened URL."""
    # Fixme: implement update logic
    raise NotImplementedError("TODO: implement update logic")


@router.delete(
    path="/{url_key}",
    name="Remove url",
    status_code=status.HTTP_201_CREATED,
)
async def delete_url(
    url: QueryLongUrl,
    # header: FromDishka[XUserHeaderDTO],
    # use_case: FromDishka[CreateUrlUseCase],
    # mapper: FromDishka[UrlPresentationMapper],
) -> SUrlResponse:
    """Creates a shortened URL."""
    # Fixme: implement delete logic
    raise NotImplementedError("TODO: implement delete logic")
