import logging
import uuid

from asyncpg import Connection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.settings.config import settings

__all__ = (
    "async_session_maker",
    "ENGINE_URL",
)

logger = logging.getLogger(__name__)
ENGINE_URL: str = str(settings.dsn)


# fix asyncpg.exceptions.InvalidSQLStatementNameError:
# prepared statement "__asyncpg_stmt_4c" does not exist
# discussion
# https://github.com/sqlalchemy/sqlalchemy/issues/6467#issuecomment-1187494311
class SQLAlchemyConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f"__asyncpg_{prefix}_{uuid.uuid4()}__"


def engine_factory() -> AsyncEngine | None:
    return create_async_engine(
        url=ENGINE_URL,
        # echo=True,
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
            "connection_class": SQLAlchemyConnection,
        },
    )


async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine_factory(),
    class_=AsyncSession,
    expire_on_commit=False,
)
