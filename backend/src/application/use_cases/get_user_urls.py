from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from src.application.dtos.users import GetUserUrlsDTO

if TYPE_CHECKING:
    from src.application.interfaces.uow import UnitOfWorkProtocol
    from src.domain.entities.url import UrlEntity

__all__ = ("GetUserUrlsUseCase",)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class GetUserUrlsUseCase:
    uow: "UnitOfWorkProtocol"

    async def execute(
        self,
        *,
        user_dto: GetUserUrlsDTO,
    ) -> list["UrlEntity"]:
        return await self.uow.repository.get_all(
            reference={"user_id": user_dto.user_id},
            limit=user_dto.pagination_data.limit,
            skip=user_dto.pagination_data.skip,
            offset=user_dto.pagination_data.offset,
        )
