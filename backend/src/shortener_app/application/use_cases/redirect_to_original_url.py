__all__ = ("RedirectToOriginalUrlUseCase",)

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

if TYPE_CHECKING:
    from shortener_app.application.dtos.urls.urls_events import (
        UrlClickedEventDTO,
    )
    from shortener_app.application.interfaces import (
        UnitOfWorkProtocol,
    )
    from shortener_app.application.mappers.url_dto_facade import UrlDtoFacade
    from shortener_app.application.services.urls.url_publisher import (
        UrlBrokerPublishService,
    )
    from shortener_app.application.services.urls.url_reader import (
        UrlReaderService,
    )

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class RedirectToOriginalUrlUseCase:
    reader_service: "UrlReaderService"
    broker_publish_service: "UrlBrokerPublishService"
    uow: "UnitOfWorkProtocol"
    mapper: "UrlDtoFacade"

    async def execute(self, key: str) -> str | None:
        async with self.uow as uow:
            entity = await self.reader_service.get_url_by_key(
                key=key,
                repository=uow.repository,
            )

        if entity is None:
            return None

        if not entity.is_active:
            # raise UrlNotActiveError(key=key)
            raise Exception("TODO: Custom not active exception")

        publish_redirected_dto = self.mapper.to_publish_redirected_dto(
            entity=entity,
        )
        asyncio.create_task(self._publish(dto=publish_redirected_dto))

        return entity.target_url

    async def _publish(self, *, dto: "UrlClickedEventDTO") -> None:
        try:
            await self.broker_publish_service.publish_update_url(dto=dto)
        except Exception:
            logger.exception(
                "Failed to publish redirected url event",
                key=dto.key,
                event_id=str(dto.event_id),
            )
