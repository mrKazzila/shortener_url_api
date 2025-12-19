__all__ = ("KafkaPublisher",)

from dataclasses import dataclass, field
from typing import Any, final

import structlog
from faststream.kafka import KafkaBroker

from src.application.dtos.urls import PublishUrlDTO
from src.application.interfaces import MessageBrokerPublisherProtocol
from src.application.mappers import UrlMapper
from src.domain.entities import UrlEntity

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class KafkaPublisher(MessageBrokerPublisherProtocol):
    """
    Kafka implementation of the MessageBrokerPublisherProtocol.
    """

    broker: KafkaBroker
    new_urls_topic: str = field(default="new-urls")
    update_urls_update_topic: str = field(default="update-urls")
    mapper: UrlMapper

    async def publish_new_url(self, entity: UrlEntity) -> None:
        try:
            publish_dto: PublishUrlDTO = self.mapper.to_publish_dto(entity)
            payload = publish_dto.to_dict()

            await self.broker.publish(
                topic=self.new_urls_topic,
                key=publish_dto.key.encode("utf-8"),
                message=payload,
                headers={"content-type": "application/json"},
            )
        except Exception as e:
            logger.error("Failed to publish new_url event", error=str(e))
            raise

    async def publish_update_url(self, payload: dict[str, Any]) -> None:
        try:
            url_key = payload.get("key")
            event_id = payload.get("event_id")

            await self.broker.publish(
                topic=self.update_urls_update_topic,
                key=url_key.encode("utf-8"),
                message=payload,
                headers={
                    "content-type": "application/json",
                    "event_id": str(event_id),
                    "event_type": "UrlClicked",
                },
            )
        except Exception as e:
            logger.error("Failed to publish update_url event", error=str(e))
            raise

    async def publish_new_urls_batch(self, entities: list[UrlEntity]) -> None:
        msgs = [self.mapper.to_publish_dto(e).to_dict() for e in entities]
        await self.broker.publish_batch(*msgs, topic=self.new_urls_topic)
