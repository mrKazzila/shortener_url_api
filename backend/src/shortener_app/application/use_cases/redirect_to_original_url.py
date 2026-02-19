__all__ = ("RedirectToOriginalUrlUseCase",)

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

if TYPE_CHECKING:
    from shortener_app.application.dtos.urls.urls_events import (
        UrlClickedEventDTO,
    )
    from shortener_app.application.mappers.url_dto_facade import UrlDtoFacade
    from shortener_app.application.use_cases.internal import (
        GetTargetByKeyUseCase,
        PublishUrlToBrokerForUpdateUseCase,
    )


logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class RedirectToOriginalUrlUseCase:
    get_target_url_by_key_uc: "GetTargetByKeyUseCase"
    publish_url_to_broker_for_update_uc: "PublishUrlToBrokerForUpdateUseCase"
    mapper: "UrlDtoFacade"

    async def execute(self, key: str) -> str | None:
        if entity := await self.get_target_url_by_key_uc.execute(key=key):
            if not entity.is_active:
                raise Exception("TODO: Custom not active exception")

            publish_redirected_dto = self.mapper.to_publish_redirected_dto(
                entity=entity,
            )
            asyncio.create_task(self._publish(dto=publish_redirected_dto))

            return entity.target_url

        return None

    async def _publish(self, *, dto: "UrlClickedEventDTO") -> None:
        try:
            await self.publish_url_to_broker_for_update_uc.execute(dto=dto)
        except Exception as exc:
            logger.exception(
                "RedirectToOriginalUrlUseCase._publish: failed to publish url %s: %s",
                dto.key,
                exc,
            )
