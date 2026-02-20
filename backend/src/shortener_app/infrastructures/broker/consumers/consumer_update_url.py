__all__ = ("run_subscriber",)

from uuid import UUID

import structlog
from dishka import AsyncContainer
from faststream import FastStream
from pydantic import BaseModel

from shortener_app.application.use_cases.process_click_url_events import (
    ApplyClickEventsUseCase,
)
from shortener_app.infrastructures.broker.consumers.common import (
    init_dependencies,
)

logger = structlog.get_logger(__name__)


class ClickEvent(BaseModel):
    key: str
    event_id: UUID


async def run_subscriber(container: AsyncContainer) -> None:
    async with container() as app_container:
        broker, update_uc = await init_dependencies(
            container=app_container,
            uc=ApplyClickEventsUseCase,
        )
        app = FastStream(broker)

        subscriber = broker.subscriber(
            "update-urls",
            group_id="update-urls-consumers",
            auto_commit=False,
            batch=True,
            max_records=500,
            batch_timeout_ms=5_000,
        )

        @subscriber
        async def _update_url(batch: list[ClickEvent]) -> None:
            events = [(msg.event_id, msg.key) for msg in batch]
            logger.info("Processing batch", size=len(events))
            await update_uc.execute(events=events)

        await app.run()
