__all__ = ("ApplyClickEventsUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final
from uuid import UUID

import structlog

if TYPE_CHECKING:
    from shortener_app.application.interfaces import UnitOfWorkProtocol

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class ApplyClickEventsUseCase:
    uow: "UnitOfWorkProtocol"

    async def execute(
        self,
        *,
        events: list[tuple[UUID, str]],
    ) -> None:
        logger.info("GOT events from broker", size=len(events))

        async with self.uow:
            inserted = await self.uow.repository.apply_click_events(
                events=events,
            )
            await self.uow.commit()

        logger.info("APPLIED events", inserted=inserted, received=len(events))
