import asyncio
import os

from alembic import context
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

from shortener_app.config.settings.logging import setup_logging
from shortener_app.infrastructures.db.models import Base

config = context.config
target_metadata = Base.metadata


def _setup_structlog_for_alembic() -> None:
    level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(level=level, json_format=True)


_setup_structlog_for_alembic()


def get_sqlalchemy_url() -> URL:
    """
    Источник истины для миграций — sqlalchemy.url из alembic config.

    В тестах ты задаёшь его через:
      cfg.set_main_option("sqlalchemy.url", "...")

    В docker/compose — через alembic.ini или env подстановку.
    """
    raw = config.get_main_option("sqlalchemy.url")
    if not raw:
        raise RuntimeError(
            "alembic sqlalchemy.url is not set. "
            "Set it in alembic.ini or via Config.set_main_option('sqlalchemy.url', ...)."
        )

    url = make_url(raw)

    # Твои миграции запускаются в async режиме — нужен async драйвер
    if url.drivername in {"postgresql", "postgres", "postgresql+psycopg", "postgresql+psycopg2"}:
        url = url.set(drivername="postgresql+asyncpg")

    return url


def run_migrations_offline() -> None:
    url = get_sqlalchemy_url()

    context.configure(
        url=str(url),
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