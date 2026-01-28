__all__ = ("AddNewUrlToCacheUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from shortener_app.application.interfaces import CacheProtocol
    from shortener_app.application.mappers import UrlMapper
    from shortener_app.domain.entities.url import UrlEntity


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AddNewUrlToCacheUseCase:
    cache: "CacheProtocol"
    mapper: "UrlMapper"

    async def execute(self, *, entity: "UrlEntity") -> bool:
        return await self.cache.set(
            key=f"short:{entity.key}",
            value=self.mapper.to_cache_dict(entity=entity),
        )
