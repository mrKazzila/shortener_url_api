__all__ = ("ProcessClickEventsUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final
from uuid import UUID

import structlog

if TYPE_CHECKING:
    from shortener_app.application.interfaces import UnitOfWorkProtocol

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class ProcessClickEventsUseCase:
    uow: "UnitOfWorkProtocol"

    async def execute(
        self,
        *,
        events: list[tuple[UUID, str]],
    ) -> None:
        if not events:
            logger.info("No click events to process")
            return

        logger.info("Got events from broker", size=len(events))

        async with self.uow as uow:
            inserted = await uow.url_repository.apply_click_events(
                events=events,
            )
            await uow.commit()

        logger.info(
            "Applied events",
            inserted=inserted,
            received=len(events),
        )
