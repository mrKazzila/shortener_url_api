__all__ = ("UnitOfWork",)

from dataclasses import dataclass
from types import TracebackType
from typing import Self, final

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from shortener_app.application.interfaces import (
    RepositoryProtocol,
    UnitOfWorkProtocol,
)

logger = structlog.get_logger(__name__)


@final
@dataclass(slots=True, kw_only=True)
class UnitOfWork(UnitOfWorkProtocol):
    session: AsyncSession
    repository: RepositoryProtocol

    tx: AsyncSessionTransaction | None = None

    async def __aenter__(self) -> Self:
        logger.debug("Starting database transaction")
        self.tx = await self.session.begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            logger.warning("Rollback transaction due to error")
            await self.rollback()

        self.tx = None

    async def commit(self) -> None:
        if self.tx is None:
            raise RuntimeError("Transaction is not started")

        logger.debug("Committing transaction")
        await self.tx.commit()
        logger.debug("Transaction committed successfully")

    async def rollback(self) -> None:
        if self.tx is None:
            return

        logger.debug("Rolling back transaction")
        await self.tx.rollback()
        logger.debug("Transaction rolled back successfully")
