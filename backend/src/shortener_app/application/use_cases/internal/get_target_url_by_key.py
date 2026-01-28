__all__ = ("GetTargetByKeyUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

from shortener_app.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from shortener_app.application.interfaces import (
        CacheProtocol,
        UnitOfWorkProtocol,
    )
    from shortener_app.application.mappers import UrlMapper

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class GetTargetByKeyUseCase:
    cache: "CacheProtocol"
    uow: "UnitOfWorkProtocol"
    mapper: "UrlMapper"

    async def execute(self, *, key: str) -> UrlEntity | None:
        if value := await self.cache.get(key=f"short:{key}"):
            return self.mapper.to_entity(
                cache={"key": key, **value},
            )
        logger.info("no cache: get from DB", key=key)

        if entity := await self.uow.repository.get(
            reference={"key": key},
        ):
            return entity
        return None
