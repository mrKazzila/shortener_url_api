__all__ = ("UpdateUrlUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

from src.application.dtos.urls import UpdateUrlDTO

if TYPE_CHECKING:
    from src.application.interfaces import (
        UnitOfWorkProtocol,
    )
    from src.application.use_cases.internal import (
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
        dto: UpdateUrlDTO,
    ) -> bool:
        if entity := await self.get_target_url_by_key_uc.execute(key=dto.key):
            updated_entity = entity.update(
                name=dto.name,
                is_active=dto.is_active,
            )
            await self.uow.repository.update(entity=updated_entity)
            await self.uow.commit()
            return True

        return False
