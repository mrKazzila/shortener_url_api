import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from src.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from src.application.interfaces.broker import (
        MessageBrokerPublisherProtocol,
    )

logger = logging.getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class PublishUrlToBrokerUseCase:
    """
    Use-case отвечает только за то, чтобы передать доменную сущность брокеру.
    Сериализация, формирование payload и протоколы — ответственность инфраструктуры.
    """

    message_broker: "MessageBrokerPublisherProtocol"

    async def execute(self, *, entity: UrlEntity) -> None:
        logger.info("PublishUrlToBrokerUseCase: received entity %r", entity)

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
