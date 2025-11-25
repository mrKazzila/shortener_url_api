import logging
import uuid

from asyncpg import Connection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

__all__ = (
    "get_session_factory",
    "engine_factory",
)

logger = logging.getLogger(__name__)


def engine_factory(
    dsn: str,
    is_echo: bool = True,
) -> AsyncEngine:
    return create_async_engine(
        url=dsn,
        echo=is_echo,
        poolclass=None,
        pool_size=4,
        max_overflow=4,
        pool_timeout=5.0,
        pool_recycle=300,
        pool_pre_ping=True,
        pool_use_lifo=True,
        json_serializer=None,
        json_deserializer=None,
        connect_args={
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
            "connection_class": _SQLAlchemyConnection,
        },
    )


def get_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


# prepared statement "__asyncpg_stmt_4c" does not exist
# discussion
# https://github.com/sqlalchemy/sqlalchemy/issues/6467#issuecomment-1187494311
class _SQLAlchemyConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f"__asyncpg_{prefix}_{uuid.uuid4()}__"
