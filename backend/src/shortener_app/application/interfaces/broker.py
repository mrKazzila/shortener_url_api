__all__ = ("MessageBrokerPublisherProtocol",)

from abc import abstractmethod
from typing import Any, Protocol

from shortener_app.domain.entities.url import UrlEntity


class MessageBrokerPublisherProtocol(Protocol):
    @abstractmethod
    async def publish_new_url(
        self,
        entity: UrlEntity,
    ) -> None: ...

    @abstractmethod
    async def publish_update_url(
        self,
        payload: dict[str, Any],
    ) -> None: ...

    @abstractmethod
    async def publish_new_urls_batch(
        self,
        entities: list[UrlEntity],
    ) -> None: ...
