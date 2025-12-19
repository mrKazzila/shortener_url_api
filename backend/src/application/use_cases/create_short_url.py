__all__ = ("CreateUrlUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

from src.application.dtos.urls import CreatedUrlDTO, CreateUrlDTO
from src.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from src.application.use_cases.internal import (
        CreateUniqKeyUseCase,
    )
    from src.infrastructures.broker.new_url_publish_queue import (
        NewUrlPublishQueue,
    )


logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUrlUseCase:
    create_uniq_key_uc: "CreateUniqKeyUseCase"
    publish_url_queue: "NewUrlPublishQueue"

    async def execute(
        self,
        *,
        dto: CreateUrlDTO,
    ) -> CreatedUrlDTO:
        key: str = await self.create_uniq_key_uc.execute(
            target_url=dto.target_url,
        )

        entity = UrlEntity.create(
            key=key,
            target_url=dto.target_url,
            user_id=dto.user_id,
        )

        await self.publish_url_queue.enqueue(entity=entity)

        return CreatedUrlDTO(
            key=entity.key,
            target_url=entity.target_url,
            user_id=entity.user_id,
        )
