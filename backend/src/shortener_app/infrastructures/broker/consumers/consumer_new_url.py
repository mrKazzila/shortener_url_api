__all__ = ("run_subscriber",)

from uuid import UUID

import structlog
from dishka import AsyncContainer
from faststream import FastStream
from pydantic import BaseModel

from shortener_app.application.use_cases.process_new_url_event import (
    ProcessNewUrlUseCase,
)
from shortener_app.domain.entities.url import UrlEntity
from shortener_app.infrastructures.broker.consumers.common import (
    init_dependencies,
)

logger = structlog.get_logger(__name__)


class NewUrlEvent(BaseModel):
    user_id: UUID
    target_url: str
    key: str


async def run_subscriber(container: AsyncContainer) -> None:
    async with container() as app_container:
        broker, process_uc = await init_dependencies(
            container=app_container,
            uc=ProcessNewUrlUseCase,
        )

        app = FastStream(broker)

        subscriber = broker.subscriber(
            "new-urls",
            group_id="new-urls-consumers",
            auto_commit=False,
            batch=True,
            max_records=1_000,
            batch_timeout_ms=5_000,
        )

        @subscriber
        async def consumer(batch: list[NewUrlEvent]) -> None:
            entities = [
                UrlEntity.create(
                    user_id=msg.user_id,
                    target_url=msg.target_url,
                    key=msg.key,
                )
                for msg in batch
            ]

            logger.info("Processing batch", size=len(entities))
            await process_uc.execute(entities=entities)

        await app.run()
