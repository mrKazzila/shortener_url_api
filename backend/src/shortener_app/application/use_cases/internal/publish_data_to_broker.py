__all__ = ("PublishUrlToBrokerUseCase",)

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
class PublishUrlToBrokerUseCase:
    message_broker: "MessageBrokerPublisherProtocol"

    async def execute(self, *, entity: "UrlEntity") -> None:
        try:
            await self.message_broker.publish_new_url(entity=entity)
            logger.info(
                "PublishUrlToBrokerUseCase: published event for key=%s",
                entity.key,
            )
        except Exception as exc:
            logger.warning(
                "PublishUrlToBrokerUseCase: failed publishing url key=%s error=%s",
                entity.key,
                exc,
            )

    async def execute_batch(self, *, entities: list["UrlEntity"]) -> None:
        await self.message_broker.publish_new_urls_batch(entities=entities)
