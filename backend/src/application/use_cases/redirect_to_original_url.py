__all__ = ("RedirectToOriginalUrlUseCase",)

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, final
from uuid import uuid4, UUID

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
            asyncio.create_task(
                self._publish(
                    entity=entity,
                    event_id=uuid4(),
                ),
            )
            return entity.target_url

        return None

    async def _publish(
        self,
        *,
        entity: "UrlEntity",
        event_id: UUID,
    ) -> None:
        try:
            await self.publish_url_to_broker_for_update_uc.execute(
                entity=entity,
                event_id=event_id,
            )
        except Exception as exc:
            logger.exception(
                "RedirectToOriginalUrlUseCase._publish: failed to publish url %s: %s",
                entity.key,
                exc,
            )
