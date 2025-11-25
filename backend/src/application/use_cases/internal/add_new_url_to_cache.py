from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from src.application._mappers.url_mapper import UrlMapper

if TYPE_CHECKING:
    from src.domain.entities.url import UrlEntity
    from src.application.interfaces.cache import CacheProtocol

__all__ = ("AddNewUrlToCacheUseCase",)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class AddNewUrlToCacheUseCase:
    cache: "CacheProtocol"

    async def execute(self, *, entity: "UrlEntity") -> bool:
        return await self.cache.set(
            key=f"short:{entity.key}",
            value=UrlMapper().to_cache_dict(entity=entity),
        )
