from dataclasses import dataclass
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from src.domain.entities.url import UrlEntity
    from src.domain.services import RandomKeyGenerator
    from src.application.use_cases.internal.check_key_in_cashe import CheckKeyInCacheUseCase
    from src.application.use_cases.internal.add_new_url_to_cache import AddNewUrlToCacheUseCase

__all__ = ("CreateUniqKeyInCacheUseCase",)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUniqKeyInCacheUseCase:
    key_generator: 'RandomKeyGenerator'
    check_key_in_cache_uc: "CheckKeyInCacheUseCase"
    add_new_url_to_cache_uc: "AddNewUrlToCacheUseCase"

    async def execute(self, *, entity: "UrlEntity") -> str:
        while True:
            key = self.key_generator()
            is_key_exist = await self.check_key_in_cache_uc.execute(key=key)

            if not is_key_exist:
                await self.add_new_url_to_cache_uc.execute(entity=entity)

                return key
