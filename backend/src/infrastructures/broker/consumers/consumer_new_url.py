import asyncio
import json
from uuid import UUID

import structlog
from faststream import FastStream
from faststream.kafka import KafkaMessage

from src.application.use_cases.internal import ProcessNewUrlUseCase
from src.config.settings.logging import setup_logging
from src.domain.entities.url import UrlEntity
from src.infrastructures.broker.consumers.common import (
    UC,
    init_container,
    init_dependencies,
)

setup_logging(json_format=True)
logger = structlog.get_logger(__name__)


async def main():
    container = await init_container()

    async with container() as app_container:
        broker, process_uc = await init_dependencies(
            container=app_container,
            us=ProcessNewUrlUseCase,
        )

        app = FastStream(broker)
        manager = BatchManager(process_uc=process_uc)

        async def consumer(msg: KafkaMessage):
            await manager.add_message(msg)

        broker.subscriber(
            "new-urls",
            group_id="new-urls-consumers",
        )(consumer)

        asyncio.create_task(manager.start_periodic())
        await app.run()


class BatchManager:
    BATCH_SIZE = 100
    FLUSH_INTERVAL = 1.0
    MAX_CONCURRENT_BATCHES = 3

    def __init__(self, *, process_uc: UC) -> None:
        self.process_uc = process_uc
        self.buffer: list[KafkaMessage] = []
        self.lock = asyncio.Lock()
        self.ongoing_tasks: set[asyncio.Task] = set()

    async def start_periodic(self) -> None:
        while True:
            await asyncio.sleep(self.FLUSH_INTERVAL)
            await self._flush()

    async def add_message(self, msg: KafkaMessage) -> None:
        async with self.lock:
            self.buffer.append(msg)
            if len(self.buffer) >= self.BATCH_SIZE:
                asyncio.create_task(self._flush())

    async def _flush(self):
        async with self.lock:
            if not self.buffer:
                return
            batch = self.buffer.copy()
            self.buffer.clear()

        await self._ensure_capacity()

        task = asyncio.create_task(self._process_batch(batch))
        self.ongoing_tasks.add(task)

        done, _ = await asyncio.wait(
            self.ongoing_tasks,
            timeout=0,
            return_when=asyncio.FIRST_COMPLETED,
        )
        self.ongoing_tasks.difference_update(done)

    async def _ensure_capacity(self) -> None:
        while len(self.ongoing_tasks) >= self.MAX_CONCURRENT_BATCHES:
            done, _ = await asyncio.wait(
                self.ongoing_tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )
            self.ongoing_tasks.difference_update(done)

    async def _process_batch(self, batch) -> None:
        try:
            entities = self._create_entities(batch=batch)
            await self.process_uc.execute(entities=entities)

            logger.info(f"Processed batch of {len(batch)} messages")
        except Exception as e:
            logger.error("Failed to process batch", error=str(e))

    @staticmethod
    def _create_entities(batch):
        dtos = [json.loads(msg.body.decode("utf-8")) for msg in batch]
        return [
            UrlEntity.create(
                user_id=UUID(dto["user_id"]),
                target_url=dto["target_url"],
                key=dto["key"],
            )
            for dto in dtos
        ]


if __name__ == "__main__":
    asyncio.run(main())
