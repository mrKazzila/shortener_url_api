__all__ = ("RedirectToOriginalUrlUseCase",)

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

if TYPE_CHECKING:
    from src.application.use_cases.internal import (
        GetTargetByKeyUseCase,
        PublishUrlToBrokerForUpdateUseCase,
    )
    from src.domain.entities.url import UrlEntity

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class RedirectToOriginalUrlUseCase:
    get_target_url_by_key_uc: "GetTargetByKeyUseCase"
    publish_url_to_broker_for_update_uc: "PublishUrlToBrokerForUpdateUseCase"

    async def execute(self, key: str) -> str | None:
        if entity := await self.get_target_url_by_key_uc.execute(key=key):
            asyncio.create_task(self._publish(entity=entity))
            return entity.target_url
        return None

    async def _publish(self, *, entity: "UrlEntity") -> None:
        try:
            logger.info(f"GOT FOR UPDATE: {entity.key=!r}")
            await self.publish_url_to_broker_for_update_uc(
                entity=entity,
                topic="update-urls",
            )
            logger.info(f"AFTER  CREATE TASK: {entity.key=!r}")
        except Exception as exc:
            logger.exception(
                "CreateUrlUseCase._publish: failed to publish url %s: %s",
                entity.key,
                exc,
            )
