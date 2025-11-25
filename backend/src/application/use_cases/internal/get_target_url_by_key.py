__all__ = ("GetTargetByKeyUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final
from uuid import UUID

import structlog

from src.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from src.application.interfaces.cache import CacheProtocol
logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class GetTargetByKeyUseCase:
    cache: "CacheProtocol"

    async def execute(self, *, key: str) -> UrlEntity | None:
        if value := await self.cache.get(key=f"short:{key}"):
            logger.info(f"FROM CACHE: {value=!r}")
            return UrlEntity.create(
                user_id=UUID(value["user_id"]),
                target_url=value["target_url"],
                key=key,
            )
        logger.info(f"NO  CACHE: {key=!r}")

        # TODO: fallback to DB
        # if model := await self.repository.get_by_key(key):
        #     return self.repository.mapper.to_entity(model)
        # return None
