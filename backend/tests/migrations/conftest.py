from __future__ import annotations

import os

import psycopg
import pytest
from alembic.config import Config

pytestmark = pytest.mark.migrations


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


@pytest.fixture(scope="session")
def alembic_cfg_nodb() -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option(
        "script_location",
        "src/shortener_app/infrastructures/db/migrations",
    )
    cfg.set_main_option(
        "sqlalchemy.url",
        "postgresql+psycopg://u:p@localhost/db",
    )
    return cfg


@pytest.fixture(scope="session")
def db_sync_dsn() -> str:
    sync_dsn = os.environ.get("DATABASE_DSN_SYNC")
    if not sync_dsn:
        pytest.skip("DATABASE_DSN_SYNC is not set in env")

    psycopg_uri = sync_dsn.replace("postgresql+psycopg://", "postgresql://", 1)
    try:
        with psycopg.connect(psycopg_uri, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
    except Exception as e:
        pytest.skip(f"Postgres not reachable: {e!r}")

    return sync_dsn


@pytest.fixture
def alembic_cfg(db_sync_dsn: str) -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option(
        "script_location",
        "src/shortener_app/infrastructures/db/migrations",
    )
    cfg.set_main_option("sqlalchemy.url", db_sync_dsn)
    return cfg


@pytest.fixture(autouse=True)
def clean_db(db_sync_dsn: str) -> None:
    psycopg_uri = db_sync_dsn.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )
    _reset_public_schema(psycopg_uri)
