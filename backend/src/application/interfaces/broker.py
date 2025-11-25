from abc import abstractmethod
from typing import Protocol

from src.domain.entities.url import UrlEntity


class MessageBrokerPublisherProtocol(Protocol):
    """
    Protocol for publishing messages to a message broker.
    """

    @abstractmethod
    async def publish_new_url(
        self,
        entity: UrlEntity,
    ) -> None: ...

    @abstractmethod
    async def publish_update_url(
        self,
        entity: UrlEntity,
        topic: str | None = None,
    ) -> None: ...
