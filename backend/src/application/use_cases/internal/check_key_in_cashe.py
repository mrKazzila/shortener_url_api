__all__ = ("CheckKeyInCacheUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from src.application.interfaces.cache import CacheProtocol


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CheckKeyInCacheUseCase:
    cache: "CacheProtocol"

    async def execute(self, key: str) -> bool:
        return await self.cache.exists(f"short:{key}")
