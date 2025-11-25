import asyncio
import json
from collections import Counter

import structlog
from dishka import make_async_container
from faststream import FastStream
from faststream.kafka import KafkaBroker, KafkaMessage

from src.application.use_cases.internal.process_url_state_update import (
    UpdateUrlUseCase,
)
from src.config.ioc.di import get_providers

logger = structlog.get_logger(__name__)

container = make_async_container(*get_providers(is_consumer=True))

BATCH_SIZE = 200
BATCH_INTERVAL = 0.2


async def batch_worker(
    queue: asyncio.Queue,
    update_url_uc: "UpdateUrlUseCase",
) -> None:
    buffer = []
    last_flush = asyncio.get_event_loop().time()

    while True:
        timeout = BATCH_INTERVAL - (
            asyncio.get_event_loop().time() - last_flush
        )
        if timeout < 0:
            timeout = 0

        try:
            item = await asyncio.wait_for(queue.get(), timeout=timeout)
            buffer.append(item)

            if len(buffer) >= BATCH_SIZE:
                await flush_buffer(buffer, update_url_uc)
                buffer.clear()
                last_flush = asyncio.get_event_loop().time()

        except TimeoutError:
            if buffer:
                await flush_buffer(buffer, update_url_uc)
                buffer.clear()
            last_flush = asyncio.get_event_loop().time()


async def flush_buffer(
    buffer: list[str],
    update_url_uc: "UpdateUrlUseCase",
) -> None:
    counter = Counter(buffer)
    logger.info("Flushing batch", size=len(buffer), unique=len(counter))
    await update_url_uc.execute(increments=counter)


async def main() -> None:
    async with container() as app_container:
        broker: KafkaBroker = await app_container.get(KafkaBroker)
        app = FastStream(broker)
        update_url_uc = await app_container.get(UpdateUrlUseCase)

        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=5000)
        asyncio.create_task(batch_worker(queue, update_url_uc))

        @broker.subscriber(
            "update_urls",
            group_id="update_urls_consumers",
        )
        async def update_url(msg: KafkaMessage):
            try:
                logger.info(f"SAVE in Queue {msg=!r}")

                data_dict = json.loads(msg.body.decode("utf-8"))
                key = data_dict.get("key")

                await queue.put(key)
                logger.info("Queued key for batch processing", key=key)

            except Exception as e:
                logger.error("Failed to process update URL", error=str(e))

        await app.run()


if __name__ == "__main__":
    asyncio.run(main())
