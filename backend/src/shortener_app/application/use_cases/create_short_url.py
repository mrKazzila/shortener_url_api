__all__ = ("CreateUrlUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

from shortener_app.application.dtos.urls.urls_cache import UrlCacheSeedDTO
from shortener_app.application.dtos.urls.urls_requests import CreateUrlDTO
from shortener_app.application.dtos.urls.urls_responses import CreatedUrlDTO
from shortener_app.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from shortener_app.application.mappers.url_dto_facade import UrlDtoFacade
    from shortener_app.application.services.urls.key_reservation import (
        UrlKeyReservationService,
    )
    from shortener_app.application.services.urls.url_enqueue import (
        UrlPublishEnqueueService,
    )


logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUrlUseCase:
    key_reservation_service: "UrlKeyReservationService"
    publish_enqueue_service: "UrlPublishEnqueueService"
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
        key: str = await self.key_reservation_service.reserve(seed=seed)

        entity = UrlEntity.create(
            key=key,
            target_url=dto.target_url,
            user_id=dto.user_id,
        )

        await self.publish_enqueue_service.enqueue_new_url(
            dto=self.mapper.to_publish_dto(entity=entity),
        )

        return self.mapper.to_created_dto(entity=entity)
