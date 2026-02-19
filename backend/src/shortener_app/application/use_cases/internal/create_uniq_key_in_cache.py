__all__ = ("CreateUniqKeyUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from shortener_app.application.dtos.urls.urls_cache import (
    UrlCacheRecordDTO,
    UrlCacheSeedDTO,
)

if TYPE_CHECKING:
    from shortener_app.application.interfaces import CacheProtocol
    from shortener_app.application.interfaces.dto_codec import DtoCodecProtocol
    from shortener_app.domain.services import RandomKeyGenerator


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUniqKeyUseCase:
    key_generator: "RandomKeyGenerator"
    cache: "CacheProtocol"
    codec: "DtoCodecProtocol"

    max_attempts: int = 50
    ttl_seconds: int | None = None

    async def execute(self, *, seed: UrlCacheSeedDTO) -> str:
        for _ in range(self.max_attempts):
            key = self.key_generator()

            record = UrlCacheRecordDTO(
                key=key,
                target_url=seed.target_url,
                user_id=seed.user_id,
                name=seed.name,
                is_active=seed.is_active,
            )

            if await self.cache.set_nx(
                key=f"short:{key}",
                value=self.codec.encode(dto=record),
                ttl_seconds=self.ttl_seconds,
            ):
                return key

        raise RuntimeError(
            "Failed to allocate unique key (too many collisions)",
        )
