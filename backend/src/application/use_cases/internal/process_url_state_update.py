from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

if TYPE_CHECKING:
    from src.application.interfaces.uow import UnitOfWorkProtocol

logger = structlog.get_logger(__name__)
__all__ = ("UpdateUrlUseCase",)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateUrlUseCase:
    uow: "UnitOfWorkProtocol"

    async def execute(self, *, increments: Counter[str]) -> None:
        logger.info(f"GOT increments from broker: {increments}")
        async with self.uow:
            await self.uow.repository.increment_clicks_batch(
                increments=increments,
            )
            await self.uow.commit()
