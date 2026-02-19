__all__ = ("NewUrlPublishQueueProtocol",)

from typing import Protocol

from shortener_app.application.dtos.urls.urls_events import PublishUrlDTO


class NewUrlPublishQueueProtocol(Protocol):
    """
    Application port for publishing new URL events asynchronously.

    The Application layer depends on this abstraction, while Infrastructure
    provides an implementation (e.g., an asyncio batching queue).
    """

    async def enqueue(self, *, dto: PublishUrlDTO) -> None:
        """Enqueue a DTO for background publishing."""
        ...
