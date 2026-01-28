__all__ = ("UnitOfWork",)

from dataclasses import dataclass
from typing import Self, final

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from shortener_app.application.interfaces import (
    RepositoryProtocol,
    UnitOfWorkProtocol,
)

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UnitOfWork(UnitOfWorkProtocol):
    session: AsyncSession
    repository: RepositoryProtocol

    async def __aenter__(self) -> Self:
        logger.debug("Starting database transaction")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            logger.warning(
                "Transaction rolled back due to exception: %s - %s",
                exc_type.__name__,
                str(exc_val),
            )
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        logger.debug("Committing transaction")
        await self.session.commit()
        logger.debug("Transaction committed successfully")

    async def rollback(self) -> None:
        logger.debug("Rolling back transaction")
        await self.session.rollback()
        logger.debug("Transaction rolled back successfully")
