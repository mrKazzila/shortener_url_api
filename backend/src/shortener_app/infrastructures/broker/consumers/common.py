__all__ = ("init_container", "init_dependencies", "UC")

from collections.abc import Iterable
from typing import TypeVar

from dishka import AsyncContainer, Provider, make_async_container
from faststream.kafka import KafkaBroker

UC = TypeVar("UC")


async def init_container(*, providers: Iterable[Provider]) -> AsyncContainer:
    """
    Build a Dishka container from a given provider list.

    NOTE:
    - This module lives in infrastructure, so it must not import config.
    - The provider list must be assembled by the entrypoint (consumers package).
    """
    return make_async_container(*providers)


async def init_dependencies(
    *,
    container: AsyncContainer,
    uc: type[UC],
) -> tuple[KafkaBroker, UC]:
    broker: KafkaBroker = await container.get(KafkaBroker)
    process_uc: UC = await container.get(uc)
    return broker, process_uc
