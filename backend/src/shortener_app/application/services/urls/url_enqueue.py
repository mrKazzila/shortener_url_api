__all__ = ("UrlPublishEnqueueService",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

if TYPE_CHECKING:
    from shortener_app.application.dtos.urls.urls_events import (
        PublishUrlDTO,
    )
    from shortener_app.application.interfaces.publish_queue import (
        NewUrlPublishQueueProtocol,
    )

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UrlPublishEnqueueService:
    new_urls_queue: "NewUrlPublishQueueProtocol"

    async def enqueue_new_url(self, *, dto: "PublishUrlDTO") -> None:
        await self.new_urls_queue.enqueue(dto=dto)
