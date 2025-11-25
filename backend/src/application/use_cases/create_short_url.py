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
        logger.info("CreateUrlUseCase.execute: received dto=%r", dto)

        entity = UrlEntity.create(
            user_id=dto.user_id,
            target_url=dto.target_url,
            key="",
        )

        key: str = await self.create_uniq_key_uc.execute(entity=entity)

        entity = dataclasses.replace(entity, key=key)
        logger.debug("CreateUrlUseCase.execute: created entity=%r", entity)

        asyncio.create_task(self._publish(entity=entity))

        created_dto = CreatedUrlDTO(
            user_id=entity.user_id,
            key=entity.key,
            target_url=entity.target_url,
        )

        logger.info(
            "CreateUrlUseCase.execute: returning created_dto=%r",
            created_dto,
        )
        return created_dto

    async def _publish(self, *, entity: UrlEntity) -> None:
        try:
            await self.publish_url_to_broker_uc.execute(entity=entity)
            logger.info(
                "CreateUrlUseCase._publish: published entity.key=%s",
                entity.key,
            )
        except Exception as exc:
            logger.exception(
                "CreateUrlUseCase._publish: failed to publish url %s: %s",
                entity.key,
                exc,
            )
