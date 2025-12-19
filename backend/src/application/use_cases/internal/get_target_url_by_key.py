__all__ = ("GetTargetByKeyUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

from src.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from src.application.interfaces import (
        CacheProtocol,
        UnitOfWorkProtocol,
    )
    from src.application.mappers import UrlMapper

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
        logger.info(f"no cache: get from DB", key=key)

        if model := await self.uow.repository.get(
            reference={"key": key},
        ):
            return model
        return None
