from dataclasses import dataclass
from typing import final

import structlog

from src.application.interfaces.broker import MessageBrokerPublisherProtocol
from src.domain.entities.url import UrlEntity

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class PublishUrlToBrokerForUpdateUseCase:
    message_broker: MessageBrokerPublisherProtocol

    async def __call__(self, *, entity: UrlEntity, topic: str) -> None:
        try:
            logger.info(f'Gotten update for {entity=!r} {topic=!r}')

            # message_broker обязан уметь принять доменную сущность
            await self.message_broker.publish_update_url(
                entity=entity,
                topic=topic,
            )
            logger.info(
                "Published update artifact event to message broker",
                key=entity.key,
            )
        except Exception as e:
            logger.warning(
                "Failed to publish artifact notification to message broker (non-critical)",
                key=entity.key,
                error=str(e),
            )
