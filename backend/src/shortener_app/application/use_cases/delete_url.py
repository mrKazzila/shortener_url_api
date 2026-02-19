__all__ = ("DeleteUrlUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

from shortener_app.application.dtos.urls.urls_requests import DeleteUrlDTO

if TYPE_CHECKING:
    from shortener_app.application.interfaces import (
        CacheProtocol,
        UnitOfWorkProtocol,
    )
    from shortener_app.application.use_cases.internal.get_target_url_by_key import (
        GetTargetByKeyUseCase,
    )

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteUrlUseCase:
    get_target_url_by_key_uc: "GetTargetByKeyUseCase"
    cache: "CacheProtocol"
    uow: "UnitOfWorkProtocol"

    async def execute(
        self,
        *,
        dto: DeleteUrlDTO,
    ) -> bool:
        if entity := await self.get_target_url_by_key_uc.execute(key=dto.key):
            await self.cache.delete(key=f"short:{entity.key}")
            await self.uow.repository.delete(entity=entity)
            await self.uow.commit()
            return True

        return False
