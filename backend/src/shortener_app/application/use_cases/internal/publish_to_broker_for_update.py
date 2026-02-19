__all__ = ("PublishUrlToBrokerForUpdateUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

if TYPE_CHECKING:
    from shortener_app.application.dtos.urls.urls_events import (
        UrlClickedEventDTO,
    )
    from shortener_app.application.interfaces import (
        MessageBrokerPublisherProtocol,
    )

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class PublishUrlToBrokerForUpdateUseCase:
    message_broker: "MessageBrokerPublisherProtocol"

    async def execute(
        self,
        *,
        dto: "UrlClickedEventDTO",
    ) -> None:
        try:
            await self.message_broker.publish_update_url(dto=dto)
            logger.info(
                "Published update event",
                key=dto.key,
                event_id=str(dto.event_id),
            )
        except Exception as e:
            logger.warning(
                "Failed to publish update event (non-critical)",
                key=dto.key,
                event_id=str(dto.event_id),
                error=str(e),
            )
