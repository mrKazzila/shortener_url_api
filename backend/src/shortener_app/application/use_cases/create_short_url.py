__all__ = ("CreateUrlUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

from shortener_app.application.dtos.urls.urls_cache import UrlCacheSeedDTO
from shortener_app.application.dtos.urls.urls_requests import CreateUrlDTO
from shortener_app.application.dtos.urls.urls_responses import CreatedUrlDTO
from shortener_app.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from shortener_app.application.interfaces.publish_queue import (
        NewUrlPublishQueueProtocol,
    )
    from shortener_app.application.mappers.url_dto_facade import UrlDtoFacade
    from shortener_app.application.use_cases.internal.create_uniq_key_in_cache import (
        CreateUniqKeyUseCase,
    )


logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUrlUseCase:
    create_uniq_key_uc: "CreateUniqKeyUseCase"
    publish_url_queue: "NewUrlPublishQueueProtocol"
    mapper: "UrlDtoFacade"

    async def execute(
        self,
        *,
        dto: CreateUrlDTO,
    ) -> CreatedUrlDTO:
        seed = UrlCacheSeedDTO(
            target_url=dto.target_url,
            user_id=dto.user_id,
            name=None,
            is_active=True,
        )
        key: str = await self.create_uniq_key_uc.execute(seed=seed)

        entity = UrlEntity.create(
            key=key,
            target_url=dto.target_url,
            user_id=dto.user_id,
        )

        publish_dto = self.mapper.to_publish_dto(entity=entity)
        await self.publish_url_queue.enqueue(dto=publish_dto)

        return self.mapper.to_created_dto(entity=entity)
