__all__ = ("MessageBrokerPublisherProtocol",)

from abc import abstractmethod
from typing import Protocol

from shortener_app.application.dtos.urls.urls_events import (
    PublishUrlDTO,
    UrlClickedEventDTO,
)


class MessageBrokerPublisherProtocol(Protocol):
    @abstractmethod
    async def publish_new_urls_batch(
        self,
        dtos: list[PublishUrlDTO],
    ) -> None: ...

    @abstractmethod
    async def publish_update_url(
        self,
        dto: UrlClickedEventDTO,
    ) -> None: ...
