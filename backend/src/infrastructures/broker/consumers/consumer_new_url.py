import asyncio
import json
from uuid import UUID

import structlog
from dishka import make_async_container
from faststream import FastStream
from faststream.kafka import KafkaBroker, KafkaMessage

from src.application.use_cases.internal import ProcessNewUrlUseCase
from src.config.ioc.di import get_providers
from src.domain.entities.url import UrlEntity

logger = structlog.get_logger(__name__)

container = make_async_container(*get_providers(is_consumer=True))

BATCH_SIZE = 100
FLUSH_INTERVAL = 1.0
MAX_CONCURRENT_BATCHES = 3


async def main():
    async with container() as app_container:
        broker: KafkaBroker = await app_container.get(KafkaBroker)
        process_new_url_uc: ProcessNewUrlUseCase = await app_container.get(
            ProcessNewUrlUseCase,
        )
        app = FastStream(broker)

        buffer: list[KafkaMessage] = []
        lock = asyncio.Lock()
        ongoing_tasks: set[asyncio.Task] = set()

        async def flush():
            nonlocal buffer
            async with lock:
                if not buffer:
                    return
                batch = buffer.copy()
                buffer.clear()

            async def process(batch_local):
                try:
                    dtos = [
                        json.loads(msg.body.decode("utf-8"))
                        for msg in batch_local
                    ]
                    entities = [
                        UrlEntity.create(
                            user_id=UUID(dto["user_id"]),
                            target_url=dto["target_url"],
                            key=dto["key"],
                        )
                        for dto in dtos
                    ]

                    await process_new_url_uc.execute(entities=entities)
                    logger.info(
                        f"Processed batch of {len(batch_local)} messages",
                    )
                except Exception as e:
                    logger.error("Failed to process batch", error=str(e))

            while len(ongoing_tasks) >= MAX_CONCURRENT_BATCHES:
                done, _ = await asyncio.wait(
                    ongoing_tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                ongoing_tasks.difference_update(done)

            task = asyncio.create_task(process(batch))
            ongoing_tasks.add(task)

            done, _ = await asyncio.wait(
                ongoing_tasks,
                timeout=0,
                return_when=asyncio.FIRST_COMPLETED,
            )
            ongoing_tasks.difference_update(done)

        async def periodic_flusher():
            while True:
                await asyncio.sleep(FLUSH_INTERVAL)
                await flush()

        asyncio.create_task(periodic_flusher())

        @broker.subscriber("new_urls", group_id="new_urls_consumers")
        async def consumer(msg: KafkaMessage):
            async with lock:
                buffer.append(msg)
                if len(buffer) >= BATCH_SIZE:
                    asyncio.create_task(flush())

        await app.run()


if __name__ == "__main__":
    asyncio.run(main())
