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



# @final
# @dataclass(frozen=True, slots=True, kw_only=True)
# class GetUserUrlsUseCase:
#     uow: "UnitOfWorkProtocol"
#
#     async def execute(
#         self,
#         *,
#         user_dto: GetUserUrlsDTO,
#     ) -> list:
#         urls = await self.uow.repository.get_all(
#             reference={"user_id": user_dto.user_id},
#             limit=user_dto.pagination_data.limit,
#             skip=user_dto.pagination_data.skip,
#             offset=user_dto.pagination_data.offset,
#         )
#
#         return [
#             DBUrlDTO(
#                 id=url.id,
#                 user_id=url.user_id,
#                 key=url.key,
#                 target_url=url.target_url,
#                 name=url.name,
#                 clicks_count=url.clicks_count,
#                 is_active=url.is_active,
#                 created_at=url.created_at,
#                 last_used=url.last_used,
#             )
#             for url in urls
#         ]
#


