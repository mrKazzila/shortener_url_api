__all__ = ("NewUrlPublishQueueAdapter",)

from dataclasses import dataclass

from shortener_app.application.dtos.urls.urls_events import PublishUrlDTO
from shortener_app.application.interfaces.publish_queue import (
    NewUrlPublishQueueProtocol,
)
from shortener_app.infrastructures.broker.new_url_publish_queue import (
    NewUrlPublishQueue,
)


@dataclass(frozen=True, slots=True)
class NewUrlPublishQueueAdapter(NewUrlPublishQueueProtocol):
    _impl: NewUrlPublishQueue

    async def enqueue(self, dto: PublishUrlDTO) -> None:
        await self._impl.enqueue(dto=dto)
