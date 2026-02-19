__all__ = ("GetUserUrlsUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

from shortener_app.application.dtos.users.user_responses import (
    GetUserUrlsResultDTO,
)

if TYPE_CHECKING:
    from shortener_app.application.dtos.users.user_requests import (
        GetUserUrlsDTO,
    )
    from shortener_app.application.interfaces import UnitOfWorkProtocol
    from shortener_app.application.mappers.url_dto_facade import UrlDtoFacade
    from shortener_app.domain.entities.url import UrlEntity


logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class GetUserUrlsUseCase:
    """
    Use-case: get paginated list of user's URLs.

    Returns Application output DTOs to keep Presentation independent of Domain entities.
    """

    uow: "UnitOfWorkProtocol"
    mapper: "UrlDtoFacade"

    async def execute(
        self,
        user_dto: "GetUserUrlsDTO",
    ) -> GetUserUrlsResultDTO:
        entities: list[UrlEntity] = await self.uow.repository.get_all(
            reference={"user_id": user_dto.user_id},
            limit=user_dto.pagination_data.limit,
            last_id=user_dto.pagination_data.last_id,
        )

        items = [self.mapper.to_user_url_item_dto(e) for e in entities]
        return GetUserUrlsResultDTO(
            items=items,
            count=len(items),
        )  # TODO: use mapper
