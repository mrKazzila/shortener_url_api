from dataclasses import dataclass
from typing import TYPE_CHECKING, final
from uuid import UUID

from src.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from src.application.interfaces.cache import CacheProtocol


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class GetTargetByKeyUseCase:
    cache: "CacheProtocol"

    async def execute(self, *, key: str) -> UrlEntity | None:
        if value := await self.cache.get(key=f"short:{key}"):
            return UrlEntity.create(
                user_id=UUID(value["user_id"]),
                target_url=value["target_url"],
                key=key,
            )

        # TODO: fallback to DB
        # if model := await self.repository.get_by_key(key):
        #     return self.repository.mapper.to_entity(model)
        # return None
