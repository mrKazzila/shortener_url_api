import logging
import uuid

from asyncpg import Connection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

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
    logger.debug("Create engine")
    try:
        return create_async_engine(
            url=ENGINE_URL,
            echo=True,
            connect_args={
                "statement_cache_size": 0,  # required by asyncpg
                "prepared_statement_cache_size": 0,  # required by asyncpg
                "connection_class": SQLAlchemyConnection,
            },
            pool_pre_ping=True,
            poolclass=NullPool,
        )
    except Exception as error_:
        logger.error("Error: %s", error_)
        return None


async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine_factory(),
    class_=AsyncSession,
    expire_on_commit=False,
)
