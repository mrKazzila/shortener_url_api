from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class ABCQueryService:
    __slots__ = ("session_factory",)

    def __init__(
        self,
        *,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.session_factory = session_factory
