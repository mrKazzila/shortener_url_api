__all__ = ("UpdateUrlUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

if TYPE_CHECKING:
    from shortener_app.application.dtos.urls.urls_requests import UpdateUrlDTO
    from shortener_app.application.interfaces import (
        UnitOfWorkProtocol,
    )
    from shortener_app.application.use_cases.internal import (
        GetTargetByKeyUseCase,
    )

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateUrlUseCase:
    get_target_url_by_key_uc: "GetTargetByKeyUseCase"
    uow: "UnitOfWorkProtocol"

    async def execute(
        self,
        *,
        dto: "UpdateUrlDTO",
    ) -> bool:
        if entity := await self.get_target_url_by_key_uc.execute(key=dto.key):
            # FIXME update cache
            async with self.uow:
                updated_entity = entity.update(
                    name=dto.name,
                    is_active=dto.is_active,
                )
                await self.uow.repository.update(entity=updated_entity)
                await self.uow.commit()
                return True

        return False
