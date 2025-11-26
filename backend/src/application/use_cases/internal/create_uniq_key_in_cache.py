__all__ = ("CreateUniqKeyUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

if TYPE_CHECKING:
    from src.application.use_cases.internal import CheckKeyInCacheUseCase
    from src.domain.services import RandomKeyGenerator

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUniqKeyUseCase:
    key_generator: "RandomKeyGenerator"
    check_key_in_cache_uc: "CheckKeyInCacheUseCase"

    async def execute(self) -> str:
        while True:
            key = self.key_generator()
            is_key_exist = await self.check_key_in_cache_uc.execute(key=key)

            if not is_key_exist:
                return key

            logger.debug("Key already exist")
