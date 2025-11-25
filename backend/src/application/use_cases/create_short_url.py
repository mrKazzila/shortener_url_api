# import asyncio
# import logging
# from dataclasses import dataclass
# from typing import TYPE_CHECKING, final
#
# from src.application.dtos.urls import CreatedUrlDTO, CreateUrlDTO, PublishUrlDTO
#
# if TYPE_CHECKING:
#     from src.application.use_cases.internal import (
#         CreateUniqKeyInCacheUseCase,
#         PublishUrlToBrokerUseCase,
#     )
#
# __all__ = ("CreateUrlUseCase",)
#
# logger = logging.getLogger(__name__)
#
#
# @final
# @dataclass(frozen=True, slots=True, kw_only=True)
# class CreateUrlUseCase:
#     create_uniq_key_uc: "CreateUniqKeyInCacheUseCase"
#     publish_url_to_broker_uc: "PublishUrlToBrokerUseCase"
#
#     async def execute(
#         self,
#         *,
#         dto: CreateUrlDTO,
#     ) -> CreatedUrlDTO:
#         logger.info(f'Gotten {dto=!r}')
#
#         key = await self.create_uniq_key_uc.execute(value=dto.to_dict())
#
#         logger.info(f'Ready to publish key {key}')
#
#         created_dto = PublishUrlDTO(
#             key=key,
#             user_id=dto.user_id,
#             target_url=dto.target_url,
#         )
#
#         asyncio.create_task(self._publish(created_dto=created_dto))
#
#         return created_dto
#
#     async def _publish(self, created_dto) -> None:
#         publish_dto = PublishUrlDTO(**created_dto.to_dict())
#         await self.publish_url_to_broker_uc(publish_dto)


# ref

# src/application/use_cases/create_short_url.py

import asyncio
import dataclasses
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from src.application.dtos.urls import CreatedUrlDTO, CreateUrlDTO
from src.domain.entities.url import UrlEntity

if TYPE_CHECKING:
    from src.application.use_cases.internal import (
        CreateUniqKeyInCacheUseCase,
        PublishUrlToBrokerUseCase,
    )

__all__ = ("CreateUrlUseCase",)

logger = logging.getLogger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUrlUseCase:
    create_uniq_key_uc: "CreateUniqKeyInCacheUseCase"
    publish_url_to_broker_uc: "PublishUrlToBrokerUseCase"

    async def execute(
        self,
        *,
        dto: CreateUrlDTO,
    ) -> CreatedUrlDTO:
        """
        1) Запрашивает уникальный ключ в кэше/сервисе генерации ключей.
        2) Создаёт доменную сущность UrlEntity (инварианты проверятся в __post_init__).
        3) Асинхронно публикует сущность в брокер (fire-and-forget).
        4) Возвращает CreatedUrlDTO, составленный из сущности.
        """
        logger.info("CreateUrlUseCase.execute: received dto=%r", dto)

        # 1) Создаём предварительную entity без ключа
        entity = UrlEntity.create(
            user_id=dto.user_id,
            target_url=dto.target_url,
            key="",  # ключ пока пустой
        )

        # 2) Генерируем уникальный ключ и сохраняем в кэш
        key: str = await self.create_uniq_key_uc.execute(entity=entity)

        # 3) Обновляем entity с реальным ключом
        entity = dataclasses.replace(entity, key=key)
        logger.debug("CreateUrlUseCase.execute: created entity=%r", entity)

        # 3) Fire-and-forget публикация сущности в брокер
        # Передаём саму сущность — пусть брокер решает, что сериализовать.
        asyncio.create_task(self._publish(entity=entity))

        # 4) Формируем и возвращаем DTO результата (CreatedUrlDTO)
        created_dto = CreatedUrlDTO(
            user_id=entity.user_id,
            key=entity.key,
            target_url=entity.target_url,
        )

        logger.info("CreateUrlUseCase.execute: returning created_dto=%r", created_dto)
        return created_dto

    async def _publish(self, *, entity: UrlEntity) -> None:
        """Вспомогательная корутина для публикации сущности в брокер."""
        try:
            await self.publish_url_to_broker_uc.execute(entity=entity)
            logger.info("CreateUrlUseCase._publish: published entity.key=%s", entity.key)
        except Exception as exc:  # логируем ошибку, но не кидаем — публикация ненадёжна
            logger.exception("CreateUrlUseCase._publish: failed to publish url %s: %s", entity.key, exc)
