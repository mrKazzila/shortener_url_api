import logging
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters import UrlsRepository
from app.service_layer.unit_of_work.abc_uow import ABCUnitOfWork
from app.settings.database import async_session_maker

__all__ = ("UnitOfWork",)
logger = logging.getLogger(__name__)


class UnitOfWork(ABCUnitOfWork):
    __slots__ = ("session_factory",)

    def __init__(self) -> None:
        self.session_factory = async_session_maker

        self._session = None
        self._urls_repo = None

    def __repr__(self) -> str:
        return f"[{self.__class__.__name__} {id(self)}]"

    @property
    def session(self) -> AsyncSession:
        if not self._session:
            self._session = self.session_factory()
        return self._session

    @property
    def urls_repo(self) -> UrlsRepository:
        if not self._urls_repo:
            self._urls_repo = UrlsRepository(session=self.session)
        return self._urls_repo

    async def __aenter__(self) -> Self:
        logger.debug(f"[x]  Start {self!r}  [x]")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.session.close()
        logger.debug(f"[x]  Closed {self!r} [x]")

    async def commit(self) -> None:
        logger.debug(f"[x]  Commit {self!r} [x]")
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
