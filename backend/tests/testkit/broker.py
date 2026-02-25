from dataclasses import dataclass, field

from shortener_app.application.dtos.urls.urls_events import (
    PublishUrlDTO,
    UrlClickedEventDTO,
)
from shortener_app.application.interfaces.broker import (
    MessageBrokerPublisherProtocol,
)


@dataclass
class FakeMessageBrokerPublisher(MessageBrokerPublisherProtocol):
    publish_new_urls_batch_calls: list[list[PublishUrlDTO]] = field(
        default_factory=list,
    )
    publish_update_url_calls: list[UrlClickedEventDTO] = field(
        default_factory=list,
    )

    raise_on_publish_new_urls_batch: Exception | None = None
    raise_on_publish_update_url: Exception | None = None

    async def publish_new_urls_batch(self, dtos: list[PublishUrlDTO]) -> None:
        self.publish_new_urls_batch_calls.append(dtos)
        if self.raise_on_publish_new_urls_batch is not None:
            raise self.raise_on_publish_new_urls_batch

    async def publish_update_url(self, dto: UrlClickedEventDTO) -> None:
        self.publish_update_url_calls.append(dto)
        if self.raise_on_publish_update_url is not None:
            raise self.raise_on_publish_update_url
