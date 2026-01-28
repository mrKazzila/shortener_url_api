__all__ = ("PublishUrlToBrokerForUpdateUseCase",)

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

if TYPE_CHECKING:
    from shortener_app.application.interfaces import (
        MessageBrokerPublisherProtocol,
    )
    from shortener_app.domain.entities.url import UrlEntity

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class PublishUrlToBrokerForUpdateUseCase:
    message_broker: "MessageBrokerPublisherProtocol"

    async def execute(
        self,
        *,
        entity: "UrlEntity",
        event_id: uuid.UUID,
    ) -> None:
        payload = {
            "event_id": str(event_id),
            "key": entity.key,
        }

        try:
            await self.message_broker.publish_update_url(payload=payload)
            logger.info(
                "Published update event",
                key=entity.key,
                event_id=str(event_id),
            )
        except Exception as e:
            logger.warning(
                "Failed to publish update event (non-critical)",
                key=entity.key,
                event_id=str(event_id),
                error=str(e),
            )
