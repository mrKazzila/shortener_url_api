import logging
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from src.application.dtos.users import (
    # noqa
    GetUserUrlsDTO,
    PaginationDTO,
)
from src.application.use_cases import GetUserUrlsUseCase
from src.presentation._mappers.user_mapper import UserPresentationMapper
from src.presentation.api.rest.schemas.users import SUserUrls

logger = logging.getLogger(__name__)

__all__ = ("router",)

router: APIRouter = APIRouter(
    tags=["users"],
    route_class=DishkaRoute,
)


@router.get(
    path="/",
    name="Get all user urls",
    status_code=status.HTTP_200_OK,
)
async def get_user_urls(
    # header: FromDishka[XUserHeaderDTO],
    use_case: FromDishka[GetUserUrlsUseCase],
) -> SUserUrls:
    """Get all user urls."""
    user_urls = await use_case.execute(
        user_dto=GetUserUrlsDTO(
            # user_id=UUID(header.x_user_id),
            user_id=UUID("3b0e3fe7-e753-4e14-9ff4-0a200c2cbdcf"),
            pagination_data=PaginationDTO(
                limit=10,
                offset=0,
                skip=0,
            ),
        ),
    )

    return UserPresentationMapper.to_response(user_urls=user_urls)
