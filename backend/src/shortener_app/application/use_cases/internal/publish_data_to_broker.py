__all__ = ("PublishUrlToBrokerUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

if TYPE_CHECKING:
    from shortener_app.application.dtos.urls.urls_events import PublishUrlDTO
    from shortener_app.application.interfaces import (
        MessageBrokerPublisherProtocol,
    )

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class PublishUrlToBrokerUseCase:
    message_broker: "MessageBrokerPublisherProtocol"

    async def execute_batch(self, *, dtos: list["PublishUrlDTO"]) -> None:
        await self.message_broker.publish_new_urls_batch(dtos=dtos)
