from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from urllib.parse import quote

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from shortener_app.infrastructures.db.session import (
    engine_factory,
    get_session_factory,
)

pytestmark = pytest.mark.integration


def _build_dsn_from_parts() -> tuple[str, str]:
    """
    Fallback: соберём DSN из DB_* если DATABASE_DSN* не заданы.
    Возвращает (async_dsn, sync_dsn).
    """
    proto = os.environ.get("DB_PROTOCOL", "postgresql+asyncpg")
    host = os.environ.get("DB_HOST", "postgres")
    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "shortener_test")
    user = os.environ.get("DB_USER", "shortener_test")
    password = os.environ.get("DB_PASSWORD", "shortener_test")

    user_q = quote(user, safe="")
    pass_q = quote(password, safe="")

    async_dsn = f"{proto}://{user_q}:{pass_q}@{host}:{port}/{name}"

    # для миграций/psycopg синхронный DSN
    sync_dsn = async_dsn
    if "+asyncpg" in sync_dsn:
        sync_dsn = sync_dsn.replace("+asyncpg", "+psycopg", 1)
    elif "postgresql://" in sync_dsn:
        sync_dsn = sync_dsn.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    return async_dsn, sync_dsn


def _reset_public_schema(psycopg_uri: str) -> None:
    with psycopg.connect(
        psycopg_uri,
        autocommit=True,
        connect_timeout=5,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS public CASCADE;")
            cur.execute("CREATE SCHEMA public;")
            cur.execute("GRANT ALL ON SCHEMA public TO CURRENT_USER;")
            cur.execute("GRANT ALL ON SCHEMA public TO public;")


def _make_alembic_cfg(sqlalchemy_url_sync: str) -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option(
        "script_location",
        "src/shortener_app/infrastructures/db/migrations",
    )
    cfg.set_main_option("sqlalchemy.url", sqlalchemy_url_sync)
    return cfg


@pytest.fixture(scope="session")
def db_urls() -> dict[str, str]:
    """
    Источник URL — env контейнера (compose env_file).
    Нужно иметь:
      DATABASE_DSN       -> postgresql+asyncpg://...
      DATABASE_DSN_SYNC  -> postgresql+psycopg://...
    Если их нет — собираем из DB_*.
    """
    async_dsn = os.environ.get("DATABASE_DSN")
    sync_dsn = os.environ.get("DATABASE_DSN_SYNC")

    if not async_dsn or not sync_dsn:
        async_dsn, sync_dsn = _build_dsn_from_parts()

    # psycopg v3 нужен URI вида postgresql://...
    psycopg_uri = sync_dsn.replace("postgresql+psycopg://", "postgresql://", 1)

    # healthcheck
    try:
        with psycopg.connect(psycopg_uri, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
    except Exception as e:
        pytest.skip(f"Postgres not reachable: {e!r}")

    return {
        "asyncpg": async_dsn,
        "sync": sync_dsn,
        "psycopg": psycopg_uri,
    }


@pytest.fixture(autouse=True)
def migrated_db(db_urls: dict[str, str]) -> None:
    """
    Перед каждым тестом:
    - чистим public schema
    - накатываем миграции до head
    """
    _reset_public_schema(db_urls["psycopg"])
    cfg = _make_alembic_cfg(db_urls["sync"])
    command.upgrade(cfg, "head")


@pytest.fixture
async def engine(db_urls: dict[str, str]) -> AsyncGenerator[AsyncEngine]:
    eng = engine_factory(db_urls["asyncpg"], is_echo=False)
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return get_session_factory(engine)


@pytest.fixture
async def session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    async with session_factory() as s:
        yield s
