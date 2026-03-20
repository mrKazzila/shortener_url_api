__all__ = ("UrlReaderService",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

from shortener_app.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from shortener_app.application.interfaces.repository import (
        RepositoryProtocol,
    )
    from shortener_app.application.services.urls.url_cache import (
        UrlCacheService,
    )

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UrlReaderService:
    cache_service: "UrlCacheService"

    async def get_url_by_key(
        self,
        *,
        key: str,
        repository: "RepositoryProtocol",
    ) -> UrlEntity | None:
        if value := await self.cache_service.get_by_key_cached(key=key):
            return value

        return await self.get_by_key_from_db(key=key, repository=repository)

    async def get_by_key_from_db(
        self,
        *,
        key: str,
        repository: "RepositoryProtocol",
    ) -> UrlEntity | None:
        return await repository.get(reference={"key": key})
