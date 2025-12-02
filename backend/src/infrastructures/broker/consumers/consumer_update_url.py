import asyncio
import json
from collections import Counter

import structlog
from faststream import FastStream
from faststream.kafka import KafkaMessage

from src.application.use_cases.internal import UpdateUrlUseCase
from src.config.settings.logging import setup_logging
from src.infrastructures.broker.consumers.common import (
    UC,
    init_container,
    init_dependencies,
)

setup_logging(json_format=True)
logger = structlog.get_logger(__name__)


async def main() -> None:
    container = await init_container()

    async with container() as app_container:
        broker, update_uc = await init_dependencies(
            container=app_container,
            us=UpdateUrlUseCase,
        )
        app = FastStream(broker)

        manager = KeyBatchManager(update_uc=update_uc)
        asyncio.create_task(manager.start_periodic_flusher())

        async def _update_url(msg: KafkaMessage):
            try:
                data = json.loads(msg.body.decode("utf-8"))
                key = data.get("key")
                logger.info("Queued key for batch processing", key=key)
                await manager.add_key(key)
            except Exception as e:
                logger.error("Failed to process update URL", error=str(e))

        broker.subscriber(
            "update-urls",
            group_id="update-urls-consumers",
        )(_update_url)

        await app.run()


class KeyBatchManager:
    BATCH_SIZE = 200
    BATCH_INTERVAL = 0.2

    def __init__(self, update_uc: UC):
        self.update_uc = update_uc
        self.buffer: list[str] = []
        self.lock = asyncio.Lock()

    async def start_periodic_flusher(self):
        while True:
            await asyncio.sleep(self.BATCH_INTERVAL)
            await self._flush()

    async def add_key(self, key: str):
        async with self.lock:
            self.buffer.append(key)
            if len(self.buffer) >= self.BATCH_SIZE:
                asyncio.create_task(self._flush())

    async def _flush(self):
        async with self.lock:
            if not self.buffer:
                return

            batch = self.buffer.copy()
            self.buffer.clear()

        await self._process_batch(batch)

    async def _process_batch(self, batch: list[str]):
        try:
            counter = Counter(batch)
            logger.info(
                "Flushing batch",
                size=len(batch),
                unique=len(counter),
            )
            await self.update_uc.execute(increments=counter)
        except Exception as e:
            logger.error("Failed to flush keys batch", error=str(e))


if __name__ == "__main__":
    asyncio.run(main())
