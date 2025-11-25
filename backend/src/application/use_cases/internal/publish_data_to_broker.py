# from dataclasses import dataclass
# from typing import final
#
# import structlog
#
# from src.application.dtos.urls import PublishUrlDTO
# from src.application.interfaces.broker import MessageBrokerPublisherProtocol
# from src.domain.entities import UrlEntity
#
# logger = structlog.get_logger(__name__)
#
#
# @final
# @dataclass(frozen=True, slots=True, kw_only=True)
# class PublishUrlToBrokerUseCase:
#     message_broker: MessageBrokerPublisherProtocol
#
#     async def execute(self, *, entity: UrlEntity) -> None:
#         try:
#             logger.info(f'Gotten {entity=!r}')
#
#             publish_dto = PublishUrlDTO(
#                 key=entity.key,
#                 user_id=entity.user_id,
#                 target_url=entity.target_url,
#             )
#
#             await self.message_broker.publish_new_url(url=publish_dto)
#             logger.info(
#                 "Published new url event to message broker",
#                 key=entity.key,
#             )
#         except Exception as e:
#             logger.warning(
#                 "Failed to publish url notification to message broker (non-critical)",
#                 key=entity.key,
#                 error=str(e),
#             )




import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from src.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from src.application.interfaces.broker import MessageBrokerPublisherProtocol

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
            # message_broker обязан уметь принять доменную сущность
            await self.message_broker.publish_new_url(entity=entity)

            logger.info(
                "PublishUrlToBrokerUseCase: published event for key=%s",
                entity.key,
            )

        except Exception as exc:
            # Падать UC не должен — публикация не критична для основной логики
            logger.warning(
                "PublishUrlToBrokerUseCase: failed publishing url key=%s error=%s",
                entity.key,
                exc,
            )
