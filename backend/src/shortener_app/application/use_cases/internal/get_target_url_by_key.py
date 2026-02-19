__all__ = ("GetTargetByKeyUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

from shortener_app.application.dtos.urls.urls_cache import UrlCacheRecordDTO
from shortener_app.application.interfaces.dto_codec import DtoCodecProtocol
from shortener_app.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from shortener_app.application.interfaces import (
        CacheProtocol,
        UnitOfWorkProtocol,
    )
    from shortener_app.application.mappers import UrlDtoFacade

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class GetTargetByKeyUseCase:
    cache: "CacheProtocol"
    uow: "UnitOfWorkProtocol"
    mapper: "UrlDtoFacade"
    codec: DtoCodecProtocol[UrlCacheRecordDTO, dict[str, str]]

    async def execute(self, *, key: str) -> UrlEntity | None:
        if value := await self.cache.get(key=f"short:{key}"):
            cache_dto: UrlCacheRecordDTO = self.codec.decode(value)
            return self.mapper.to_entity_from_cache_dto(dto=cache_dto)

        logger.info("no cache: get from DB", key=key)
        return await self.uow.repository.get(reference={"key": key})
