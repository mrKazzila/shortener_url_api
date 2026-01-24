__all__ = ("CreateUniqKeyUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from src.application.dtos.urls import CreateUrlDTO
    from src.application.interfaces import CacheProtocol
    from src.domain.services import RandomKeyGenerator


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
        dto: "CreateUrlDTO",
    ) -> str:
        try:
            cache_value = dto.to_dict()
        except (AttributeError, TypeError, ValueError) as e:
            # TODO: CustomError
            raise RuntimeError(f"DTO serialization error: {e}")

        for _ in range(self.max_attempts):
            key = self.key_generator()

            if await self.cache.set_nx(
                key=f"short:{key}",
                value=cache_value,
                ttl_seconds=self.ttl_seconds,
            ):
                return key

        # TODO: CustomError
        raise RuntimeError(
            "Failed to allocate unique key (too many collisions)",
        )
