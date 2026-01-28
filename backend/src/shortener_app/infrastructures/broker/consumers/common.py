__all__ = ("init_container", "init_dependencies", "UC")

from typing import TypeVar

from dishka import AsyncContainer, make_async_container
from faststream.kafka import KafkaBroker

from shortener_app.config.ioc.di import get_providers

UC = TypeVar("UC")


async def init_container():
    return make_async_container(
        *get_providers(is_consumer=True),
    )


async def init_dependencies(
    *,
    container: AsyncContainer,
    uc: UC,
) -> tuple[KafkaBroker, UC]:
    broker: KafkaBroker = await container.get(KafkaBroker)
    process_uc: UC = await container.get(uc)
    return broker, process_uc
