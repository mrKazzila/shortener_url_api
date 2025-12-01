__all__ = ("router",)

from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status

from src.application.dtos.users import (
    # noqa
    GetUserUrlsDTO,
    PaginationDTO,
)
from src.application.use_cases import GetUserUrlsUseCase
from src.presentation.api.schemas.pagination import (
    PaginationParams,
    pagination_params,
)
from src.presentation.api.schemas.users import SUserUrls
from src.presentation.mappers.user_mapper import UserPresentationMapper

router: APIRouter = APIRouter(
    prefix="/users",
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
    mapper: FromDishka[UserPresentationMapper],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
) -> SUserUrls:
    """Get all user urls."""
    user_urls = await use_case.execute(
        user_dto=GetUserUrlsDTO(
            # user_id=UUID(header.x_user_id),
            user_id=UUID("3b0e3fe7-e753-4e14-9ff4-0a200c2cbdcf"),
            pagination_data=PaginationDTO(
                limit=pagination.limit,
                last_id=pagination.last_id,
            ),
        ),
    )

    return mapper.to_response(user_urls=user_urls)
