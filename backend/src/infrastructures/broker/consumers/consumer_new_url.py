# import asyncio
#
# import structlog
# from dishka import make_async_container
# from faststream import FastStream
# from faststream.kafka import KafkaBroker, KafkaMessage
#
# from src.config.ioc.di import get_providers
# from src.application.use_cases.internal.process_new_url import ProcessNewUrlUseCase
#
# logger = structlog.get_logger(__name__)
#
# container = make_async_container(*get_providers(is_consumer=True))
#
#
# async def main():
#     async with container() as app_container:
#         broker: KafkaBroker = await app_container.get(KafkaBroker)
#         app = FastStream(broker)
#
#         process_new_url_uc = await app_container.get(ProcessNewUrlUseCase)
#
#         @broker.subscriber(
#             "new_urls",
#             group_id="new_urls_consumers",
#         )
#         async def handle_new_url(msg: KafkaMessage):
#             try:
#                 await process_new_url_uc.execute(dto=msg.body)
#                 logger.info("Processed new URL successfully", msg=msg.body)
#             except Exception as e:
#                 logger.error("Failed to process new URL", error=str(e))
#
#         await app.run()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())


# type2
import asyncio
import json
from typing import List
from uuid import UUID

import structlog
from dishka import make_async_container
from faststream import FastStream
from faststream.kafka import KafkaBroker, KafkaMessage

from src.application.use_cases.internal.process_new_url import ProcessNewUrlUseCase
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
        process_new_url_uc: ProcessNewUrlUseCase = await app_container.get(ProcessNewUrlUseCase)
        app = FastStream(broker)

        buffer: List[KafkaMessage] = []
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
                    dtos = [json.loads(msg.body.decode("utf-8")) for msg in batch_local]
                    # Преобразуем dict в entity (id=None)
                    entities = [
                        UrlEntity.create(
                            user_id=UUID(dto["user_id"]),
                            target_url=dto["target_url"],
                            key=dto["key"],
                        )
                        for dto in dtos
                    ]
                    await process_new_url_uc.execute(entities=entities)
                    logger.info(f"Processed batch of {len(batch_local)} messages")
                except Exception as e:
                    logger.error("Failed to process batch", error=str(e))

            # ограничиваем параллельную обработку
            while len(ongoing_tasks) >= MAX_CONCURRENT_BATCHES:
                done, _ = await asyncio.wait(
                    ongoing_tasks, return_when=asyncio.FIRST_COMPLETED
                )
                ongoing_tasks.difference_update(done)

            task = asyncio.create_task(process(batch))
            ongoing_tasks.add(task)

            # удаляем завершившиеся задачи без ожидания
            done, _ = await asyncio.wait(
                ongoing_tasks, timeout=0, return_when=asyncio.FIRST_COMPLETED
            )
            ongoing_tasks.difference_update(done)

        async def periodic_flusher():
            while True:
                await asyncio.sleep(FLUSH_INTERVAL)
                await flush()

        # авто-флешер
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

# type3
# import asyncio
# import json
# import structlog
# from typing import List, Set
#
# from dishka import make_async_container
# from faststream import FastStream
# from faststream.kafka import KafkaBroker, KafkaMessage
#
# from src.application.use_cases.internal.process_new_url import ProcessNewUrlUseCase
# from src.config.ioc.di import get_providers
#
# logger = structlog.get_logger(__name__)
#
# container = make_async_container(*get_providers(is_consumer=True))
#
# BATCH_SIZE = 100
# FLUSH_INTERVAL = 1.0  # секунды
# MAX_CONCURRENT_BATCHES = 3  # параллельных батчей
#
#
# async def main():
#     async with container() as app_container:
#         broker: KafkaBroker = await app_container.get(KafkaBroker)
#         process_new_url_uc: ProcessNewUrlUseCase = await app_container.get(ProcessNewUrlUseCase)
#         app = FastStream(broker)
#
#         buffer: List[KafkaMessage] = []
#         lock = asyncio.Lock()
#         ongoing_tasks: Set[asyncio.Task] = set()
#         periodic_tasks: List[asyncio.Task] = []
#
#         async def process_batch(batch: List[KafkaMessage]):
#             """Обработка одного батча и запись в БД."""
#             try:
#                 dtos = [json.loads(msg.body.decode("utf-8")) for msg in batch]
#                 await process_new_url_uc.execute(dto=dtos)
#                 logger.info(f"Processed batch of {len(batch)} messages")
#             except Exception as e:
#                 logger.error("Failed to process batch", error=str(e))
#
#         async def flush():
#             """Сброс текущего буфера в обработку."""
#             async with lock:
#                 if not buffer:
#                     return
#                 batch = buffer.copy()
#                 buffer.clear()
#
#             # Ограничиваем параллелизм
#             while len(ongoing_tasks) >= MAX_CONCURRENT_BATCHES:
#                 done, _ = await asyncio.wait(ongoing_tasks, return_when=asyncio.FIRST_COMPLETED)
#                 ongoing_tasks.difference_update(done)
#
#             task = asyncio.create_task(process_batch(batch))
#             ongoing_tasks.add(task)
#
#             # Убираем завершившиеся задачи без ожидания
#             done, _ = await asyncio.wait(ongoing_tasks, timeout=0, return_when=asyncio.FIRST_COMPLETED)
#             ongoing_tasks.difference_update(done)
#
#         async def periodic_flusher():
#             """Флешер, который регулярно сбрасывает буфер."""
#             try:
#                 while True:
#                     await asyncio.sleep(FLUSH_INTERVAL)
#                     await flush()
#             except asyncio.CancelledError:
#                 # Флешер отменён, перед shutdown добиваем оставшиеся
#                 await flush()
#                 raise
#
#         async def startup_hook():
#             """Запускаем периодический флешер в фоне."""
#             task = asyncio.create_task(periodic_flusher())
#             periodic_tasks.append(task)
#
#         async def shutdown_hook():
#             """При shutdown останавливаем флешер и ждем завершения всех задач."""
#             for t in periodic_tasks:
#                 t.cancel()
#             # ждём их завершения, игнорируя ошибки CancelledError
#             await asyncio.gather(*periodic_tasks, return_exceptions=True)
#
#             # добиваем оставшиеся сообщения
#             await flush()
#             if ongoing_tasks:
#                 await asyncio.gather(*ongoing_tasks, return_exceptions=True)
#
#         app.on_startup(startup_hook)
#         app.on_shutdown(shutdown_hook)
#
#         @broker.subscriber("new_urls", group_id="new_urls_consumers")
#         async def consumer(msg: KafkaMessage):
#             """Добавляем сообщение в буфер и запускаем flush по размеру батча."""
#             async with lock:
#                 buffer.append(msg)
#                 if len(buffer) >= BATCH_SIZE:
#                     asyncio.create_task(flush())
#
#         # Запускаем FastStream
#         await app.run()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
