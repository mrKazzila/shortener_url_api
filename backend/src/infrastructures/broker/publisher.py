__all__ = ("KafkaPublisher",)

import json
from dataclasses import dataclass, field
from typing import final

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
    Publishes artifact admission notifications to a Kafka topic.
    """

    broker: KafkaBroker
    default_topic: str = field(default="new-urls")
    mapper: UrlMapper

    async def publish_update_url(
        self,
        entity: UrlEntity,
        topic: str | None = None,
    ) -> None:
        try:
            publish_dto: PublishUrlDTO = self.mapper.to_publish_dto(
                entity,
            )

            await self.broker.publish(
                key=publish_dto.key.encode("utf-8"),
                message=json.dumps(publish_dto.to_dict(), ensure_ascii=False),
                topic=topic,
            )

        except Exception as e:
            logger.error("Failed to publish artifact", error=str(e))
            raise

    async def publish_new_url(
        self,
        entity: UrlEntity,
    ) -> None:
        try:
            publish_dto: PublishUrlDTO = self.mapper.to_publish_dto(
                entity,
            )

            await self.broker.publish(
                key=publish_dto.key.encode("utf-8"),
                message=json.dumps(publish_dto.to_dict(), ensure_ascii=False),
                topic=self.default_topic,
            )

        except Exception as e:
            logger.error("Failed to publish artifact", error=str(e))
            raise
