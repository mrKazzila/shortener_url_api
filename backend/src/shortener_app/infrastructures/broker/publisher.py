__all__ = ("KafkaPublisher",)

from dataclasses import dataclass, field
from typing import final

import structlog
from faststream.kafka import KafkaBroker

from shortener_app.application.dtos.urls.urls_events import (
    PublishUrlDTO,
    UrlClickedEventDTO,
)
from shortener_app.application.interfaces import MessageBrokerPublisherProtocol
from shortener_app.application.interfaces.dto_codec import DtoCodecProtocol

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class KafkaPublisher(MessageBrokerPublisherProtocol):
    """
    Kafka publisher adapter.

    Uses dedicated codecs per message type to keep schemas explicit and type-safe.
    """

    broker: KafkaBroker

    publish_url_codec: DtoCodecProtocol[PublishUrlDTO, bytes]
    url_clicked_codec: DtoCodecProtocol[UrlClickedEventDTO, bytes]

    new_urls_topic: str = field(default="new-urls")
    update_urls_update_topic: str = field(default="update-urls")

    async def publish_new_urls_batch(self, dtos: list[PublishUrlDTO]) -> None:
        messages = [self.publish_url_codec.encode(dto) for dto in dtos]
        await self.broker.publish_batch(*messages, topic=self.new_urls_topic)

    async def publish_update_url(self, dto: UrlClickedEventDTO) -> None:
        try:
            payload = self.url_clicked_codec.encode(dto)

            await self.broker.publish(
                topic=self.update_urls_update_topic,
                key=dto.key.encode("utf-8"),
                message=payload,
                headers={
                    "content-type": "application/json",
                    "event_id": str(dto.event_id),
                    "event_type": "UrlClicked",
                },
            )
        except Exception as e:
            logger.error("Failed to publish update_url event", error=str(e))
            raise
