__all__ = ("CreateUniqKeyUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from src.domain.services import RandomKeyGenerator
    from src.application.interfaces import CacheProtocol


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUniqKeyUseCase:
    key_generator: "RandomKeyGenerator"
    cache: "CacheProtocol"
    max_attempts: int = 50
    ttl_seconds: int | None = None

    async def execute(
        self,
        *,
        target_url: str,
    ) -> str:
        for _ in range(self.max_attempts):
            key = self.key_generator()

            if await self.cache.set_nx(
                f"short:{key}",
                {"target_url": target_url},
                ttl_seconds=self.ttl_seconds,
            ):
                return key

        # TODO: CustomError
        raise RuntimeError("Failed to allocate unique key (too many collisions)")
