__all__ = ("ProcessNewUrlUseCase",)

from dataclasses import dataclass
from typing import final

import structlog

from src.application.interfaces.uow import UnitOfWorkProtocol
from src.domain.entities import UrlEntity

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class ProcessNewUrlUseCase:
    uow: UnitOfWorkProtocol

    async def execute(self, *, entities: list[UrlEntity]) -> None:
        logger.info(f"GOTTEN {entities=!r} FROM BROKER")

        async with self.uow:
            await self.uow.repository.add_bulk(entities=entities)
            await self.uow.commit()
