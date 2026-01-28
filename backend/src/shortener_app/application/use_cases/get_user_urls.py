__all__ = ("GetUserUrlsUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

if TYPE_CHECKING:
    from shortener_app.application.dtos.users import GetUserUrlsDTO
    from shortener_app.application.interfaces import UnitOfWorkProtocol
    from shortener_app.domain.entities.url import UrlEntity


logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class GetUserUrlsUseCase:
    uow: "UnitOfWorkProtocol"

    async def execute(
        self,
        *,
        user_dto: "GetUserUrlsDTO",
    ) -> list["UrlEntity"]:
        return await self.uow.repository.get_all(
            reference={"user_id": user_dto.user_id},
            limit=user_dto.pagination_data.limit,
            last_id=user_dto.pagination_data.last_id,
        )
