import asyncio
from uuid import UUID

import structlog
from faststream import FastStream
from pydantic import BaseModel

from src.application.use_cases.internal import UpdateUrlUseCase
from src.config.settings.logging import setup_logging
from src.infrastructures.broker.consumers.common import (
    init_container,
    init_dependencies,
)

setup_logging(json_format=True)
logger = structlog.get_logger(__name__)


class ClickEvent(BaseModel):
    event_id: UUID
    key: str


async def main() -> None:
    container = await init_container()

    async with container() as app_container:
        broker, update_uc = await init_dependencies(
            container=app_container,
            uc=UpdateUrlUseCase,
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


if __name__ == "__main__":
    asyncio.run(main())
