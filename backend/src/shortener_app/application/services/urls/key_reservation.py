__all__ = ("UrlKeyReservationService",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from shortener_app.application.dtos.urls.urls_cache import (
    UrlCacheRecordDTO,
    UrlCacheSeedDTO,
)

if TYPE_CHECKING:
    from shortener_app.application.services.urls.url_cache import (
        UrlCacheService,
    )
    from shortener_app.domain.services.key_generator import RandomKeyGenerator


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UrlKeyReservationService:
    key_generator: "RandomKeyGenerator"
    cache_service: "UrlCacheService"

    max_attempts: int = 50
    ttl_seconds: int | None = None

    async def reserve(
        self,
        *,
        seed: UrlCacheSeedDTO,
    ) -> str:
        for _ in range(self.max_attempts):
            key = self.key_generator()

            record = UrlCacheRecordDTO(
                key=key,
                target_url=seed.target_url,
                user_id=seed.user_id,
                name=seed.name,
                is_active=seed.is_active,
            )

            if await self.cache_service.set_new_url(
                key=key,
                dto=record,
            ):
                return key

        raise RuntimeError(
            "Failed to allocate unique key (too many collisions)",
        )
