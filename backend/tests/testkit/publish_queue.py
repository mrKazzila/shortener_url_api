from dataclasses import dataclass, field

from shortener_app.application.dtos.urls.urls_events import PublishUrlDTO
from shortener_app.application.interfaces.publish_queue import (
    NewUrlPublishQueueProtocol,
)


@dataclass
class SpyNewUrlPublishQueue(NewUrlPublishQueueProtocol):
    calls: list[PublishUrlDTO] = field(default_factory=list)
    exc: Exception | None = None

    async def enqueue(self, *, dto: PublishUrlDTO) -> None:
        self.calls.append(dto)
        if self.exc is not None:
            raise self.exc
