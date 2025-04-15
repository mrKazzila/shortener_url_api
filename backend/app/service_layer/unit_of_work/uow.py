import logging
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters import UrlsRepository
from app.exceptions.uow import ImproperUoWUsageError
from app.service_layer.unit_of_work.abc_uow import ABCUnitOfWork

__all__ = ("UnitOfWork",)

logger = logging.getLogger(__name__)


class UnitOfWork(ABCUnitOfWork):
    __slots__ = ("_session", "_urls_repo")
    NONE_OBJECT_ID = 0

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_factory = session_factory
        self._session = None
        self._urls_repo = None

    def __repr__(self) -> str:
        session_id = (
            id(self._session) if self._session else self.NONE_OBJECT_ID
        )
        url_repo_id = (
            id(self.urls_repo) if self._urls_repo else self.NONE_OBJECT_ID
        )

        return (
            f"[{self.__class__.__name__} object_id={id(self)} "
            f"session_id={session_id}, url_repo_id={url_repo_id}]"
        )

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise ImproperUoWUsageError()
        return self._session

    @property
    def urls_repo(self) -> UrlsRepository:
        if not self._urls_repo:
            self._urls_repo = UrlsRepository(session=self.session)
        return self._urls_repo

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        logger.debug("[x]  Start %r  [x]", self)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._session is not None:
            if exc_type is not None:
                await self._session.rollback()

            logger.debug("[x]  Closing %r  [x]", self)
            await self._session.close()
            self._session = None

        logger.debug("[x]  Closed %r  [x]", self)

    async def commit(self) -> None:
        logger.debug("[x]  Commit %r  [x]", self)
        await self.session.commit()

    async def rollback(self) -> None:
        logger.debug("[x]  Rollback %r  [x]", self)
        await self.session.rollback()
