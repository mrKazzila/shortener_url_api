import asyncio
import time
from dataclasses import dataclass
from typing import Final, Optional

import structlog

from src.domain.entities.url import UrlEntity

logger = structlog.get_logger(__name__)

_STOP: Final[object] = object()


@dataclass(slots=True)
class NewUrlItem:
    entity: UrlEntity


class NewUrlPublishQueue:
    def __init__(
        self,
        *,
        publish_uc,
        maxsize: int = 10_000,
        workers: int = 4,
        enqueue_timeout_sec: float = 0.01,
        max_retries: int = 5,
        base_backoff_sec: float = 0.05,
        report_interval_sec: float = 1.0,
        batch_size: int = 200,
        batch_window_sec: float = 0.2,
    ) -> None:
        self._publish_uc = publish_uc
        self._q: asyncio.Queue[object] = asyncio.Queue(maxsize=maxsize)

        self._workers = workers
        self._enqueue_timeout_sec = enqueue_timeout_sec

        self._max_retries = max_retries
        self._base_backoff_sec = base_backoff_sec

        self._report_interval_sec = report_interval_sec
        self._batch_size = batch_size
        self._batch_window_sec = batch_window_sec

        self._tasks: list[asyncio.Task] = []
        self._report_task: Optional[asyncio.Task] = None
        self._started = False

        self._enqueued = 0
        self._enqueue_timeouts = 0

        self._publish_calls = 0
        self._published_msgs = 0
        self._retries = 0
        self._failures = 0

        self._publish_call_ms_sum = 0.0
        self._publish_call_ms_max = 0.0

        self._last_qsize = 0

    async def start(self) -> None:
        if self._started:
            return None

        self._started = True

        for i in range(self._workers):
            self._tasks.append(
                asyncio.create_task(
                    self._worker(i),
                    name=f"new-url-pub-{i}",
                ),
            )

        self._report_task = asyncio.create_task(
            self._reporter(),
            name="new-url-pub-reporter",
        )

        logger.info(
            "NewUrlPublishQueue started",
            workers=self._workers,
            maxsize=self._q.maxsize,
            enqueue_timeout_sec=self._enqueue_timeout_sec,
            batch_size=self._batch_size,
            batch_window_sec=self._batch_window_sec,
            max_retries=self._max_retries,
            base_backoff_sec=self._base_backoff_sec,
        )
        return None

    async def stop(
        self,
        *,
        drain: bool = True,
        timeout_sec: float = 10.0,
    ) -> None:
        if not self._started:
            return None

        logger.info(
            "NewUrlPublishQueue stopping",
            drain=drain,
            timeout_sec=timeout_sec,
            qsize=self._q.qsize(),
        )

        if drain:
            try:
                await asyncio.wait_for(self._q.join(), timeout=timeout_sec)
            except asyncio.TimeoutError:
                logger.warning(
                    "NewUrlPublishQueue drain timeout",
                    timeout_sec=timeout_sec,
                    qsize=self._q.qsize(),
                )

        if self._report_task is not None:
            self._report_task.cancel()
            try:
                await self._report_task
            except asyncio.CancelledError:
                pass
            self._report_task = None

        for _ in range(self._workers):
            await self._q.put(_STOP)

        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        self._started = False

        logger.info("NewUrlPublishQueue stopped")
        return None

    async def enqueue(self, *, entity: UrlEntity) -> None:
        item = NewUrlItem(entity=entity)

        try:
            self._q.put_nowait(item)
            self._enqueued += 1
            return None
        except asyncio.QueueFull:
            pass

        try:
            await asyncio.wait_for(self._q.put(item), timeout=self._enqueue_timeout_sec)
            self._enqueued += 1
            return None
        except asyncio.TimeoutError:
            self._enqueue_timeouts += 1
            qsize = self._q.qsize()

            if qsize >= int(self._q.maxsize * 0.8):
                logger.warning(
                    "Publish queue overloaded; applying backpressure",
                    key=entity.key,
                    qsize=qsize,
                    maxsize=self._q.maxsize,
                )

            await self._q.put(item)
            self._enqueued += 1

    async def _worker(self, idx: int) -> None:
        while True:
            first = await self._q.get()
            consumed = 1
            stop_after = False

            entities: list[UrlEntity] = []

            try:
                if first is _STOP:
                    return None

                assert isinstance(first, NewUrlItem)
                entities.append(first.entity)

                deadline = time.perf_counter() + self._batch_window_sec

                while len(entities) < self._batch_size:
                    remaining = deadline - time.perf_counter()
                    if remaining <= 0:
                        break

                    try:
                        nxt = await asyncio.wait_for(self._q.get(), timeout=remaining)
                    except asyncio.TimeoutError:
                        break

                    consumed += 1

                    if nxt is _STOP:
                        stop_after = True
                        break

                    assert isinstance(nxt, NewUrlItem)
                    entities.append(nxt.entity)

                await self._publish_with_retries(entities, worker=idx)

            finally:
                for _ in range(consumed):
                    self._q.task_done()

            if stop_after:
                return None

    @staticmethod
    def _is_batch_buffer_full_error(err: Exception) -> bool:
        msg = str(err).lower()
        return "batch buffer is full" in msg or "buffer is full" in msg

    async def _publish_with_retries(
        self,
        entities: list[UrlEntity],
        *,
        worker: int,
    ) -> None:
        if not entities:
            return None

        last_err: Optional[Exception] = None

        for attempt in range(1, self._max_retries + 1):
            t0 = time.perf_counter()
            try:
                await self._publish_uc.execute_batch(entities=entities)

                dt_ms = (time.perf_counter() - t0) * 1000.0
                self._publish_calls += 1
                self._published_msgs += len(entities)
                self._publish_call_ms_sum += dt_ms
                self._publish_call_ms_max = max(self._publish_call_ms_max, dt_ms)
                return None

            except Exception as e:
                last_err = e

                if self._is_batch_buffer_full_error(e) and len(entities) > 1:
                    mid = len(entities) // 2
                    left = entities[:mid]
                    right = entities[mid:]

                    logger.warning(
                        "Publish batch overflow; splitting",
                        worker=worker,
                        original_batch_size=len(entities),
                        left_size=len(left),
                        right_size=len(right),
                        error=str(e),
                    )

                    await self._publish_with_retries(left, worker=worker)
                    await self._publish_with_retries(right, worker=worker)
                    return None

                self._retries += 1
                dt_ms = (time.perf_counter() - t0) * 1000.0
                sleep_for = self._base_backoff_sec * (2 ** (attempt - 1))

                logger.warning(
                    "Publish batch failed; retrying",
                    worker=worker,
                    attempt=attempt,
                    batch_size=len(entities),
                    publish_ms=round(dt_ms, 2),
                    sleep_for=sleep_for,
                    error=str(e),
                )
                await asyncio.sleep(sleep_for)

        self._failures += 1
        logger.error(
            "Publish batch failed permanently",
            worker=worker,
            batch_size=len(entities),
            error=str(last_err),
        )
        return None

    async def _reporter(self) -> None:
        try:
            while True:
                await asyncio.sleep(self._report_interval_sec)

                qsize = self._q.qsize()
                growing = qsize > self._last_qsize
                self._last_qsize = qsize

                calls = self._publish_calls
                msgs = self._published_msgs

                avg_call_ms = self._publish_call_ms_sum / calls if calls else 0.0
                avg_msg_ms = self._publish_call_ms_sum / msgs if msgs else 0.0
                avg_batch = msgs / calls if calls else 0.0

                logger.error(
                    "NewUrlPublishQueue stats",
                    qsize=qsize,
                    maxsize=self._q.maxsize,
                    backlog_growing=growing,
                    enqueued_per_interval=self._enqueued,
                    enqueue_timeouts_per_interval=self._enqueue_timeouts,
                    published_msgs_per_interval=msgs,
                    publish_calls_per_interval=calls,
                    avg_batch_size=round(avg_batch, 2),
                    publish_call_avg_ms=round(avg_call_ms, 2),
                    publish_call_max_ms=round(self._publish_call_ms_max, 2),
                    publish_per_msg_avg_ms=round(avg_msg_ms, 6),
                    retries_per_interval=self._retries,
                    failures_per_interval=self._failures,
                    batch_size=self._batch_size,
                    batch_window_sec=self._batch_window_sec,
                )

                self._enqueued = 0
                self._enqueue_timeouts = 0
                self._publish_calls = 0
                self._published_msgs = 0
                self._retries = 0
                self._failures = 0
                self._publish_call_ms_sum = 0.0
                self._publish_call_ms_max = 0.0

        except asyncio.CancelledError:
            return None
