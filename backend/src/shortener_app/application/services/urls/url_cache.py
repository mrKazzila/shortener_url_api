__all__ = ("UrlCacheService",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from shortener_app.application.dtos.urls.urls_cache import (
    UrlCacheRecordDTO,
)
from shortener_app.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from shortener_app.application.interfaces.cache import CacheProtocol
    from shortener_app.application.interfaces.dto_codec import DtoCodecProtocol
    from shortener_app.application.mappers.url_dto_facade import UrlDtoFacade


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UrlCacheService:
    cache: "CacheProtocol"
    codec: "DtoCodecProtocol"
    mapper: "UrlDtoFacade"

    max_attempts: int = 50
    ttl_seconds: int | None = None

    async def set_new_url(
        self,
        *,
        key: str,
        dto: UrlCacheRecordDTO,
    ) -> str | bool:
        if await self.cache.set_nx(
            key=self._key(key=key),
            value=self.codec.encode(dto=dto),
            ttl_seconds=self.ttl_seconds,
        ):
            return key
        return False

    async def get_by_key_cached(
        self,
        *,
        key: str,
    ) -> UrlEntity | None:
        if value := await self.cache.get(key=self._key(key=key)):
            dto = self.codec.decode(value)
            return self.mapper.to_entity_from_cache_dto(dto=dto)
        return None

    async def delete_by_key(
        self,
        *,
        key: str,
    ) -> None:
        await self.cache.delete(key=self._key(key=key))

    @staticmethod
    def _key(key: str) -> str:
        return f"short:{key}"
