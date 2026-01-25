import asyncio
import os

from alembic import context
from sqlalchemy.engine import URL
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

from src.config.settings.loader import get_settings
from src.config.settings.logging import setup_logging
from src.infrastructures.db.models import Base

settings = get_settings()
config = context.config
target_metadata = Base.metadata


def _setup_structlog_for_alembic() -> None:
    level = os.getenv("LOG_LEVEL", "INFO")
    json_format = os.getenv("LOG_JSON", "0") in {
        "1",
        "true",
        "True",
        "yes",
        "YES",
    }

    setup_logging(level=level, json_format=json_format)


_setup_structlog_for_alembic()


def get_sqlalchemy_url() -> URL:
    url = make_url(str(settings.sqlalchemy_database_uri))

    if url.drivername in {"postgresql", "postgres"}:
        url = url.set(drivername="postgresql+asyncpg")

    return url


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_sqlalchemy_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable: AsyncEngine = create_async_engine(
        get_sqlalchemy_url(),
        poolclass=NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
