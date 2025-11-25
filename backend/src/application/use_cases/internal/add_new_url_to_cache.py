__all__ = ("AddNewUrlToCacheUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from src.application.interfaces.cache import CacheProtocol
    from src.application.mappers.url_mapper import UrlMapper
    from src.domain.entities.url import UrlEntity


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
