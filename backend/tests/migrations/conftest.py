import re
from collections.abc import Generator
from typing import Any

import psycopg
import pytest
from alembic.config import Config
from testcontainers.postgres import PostgresContainer


def _to_psycopg_uri(url: str) -> str:
    """
    psycopg v3 accepts URIs of the form postgresql://...
    testcontainers sometimes returns postgresql+psycopg2://..., which psycopg does not understand.
    """
    url = url.replace("postgres://", "postgresql://")
    url = re.sub(r"^postgresql\+[^:]+://", "postgresql://", url)
    return url


def _to_sqlalchemy_url(url: str) -> str:
    """
    For Alembic/SQLAlchemy, you need a URL like postgresql+psycopg://...
    """
    url = url.replace("postgres://", "postgresql://")
    url = re.sub(r"^postgresql\+[^:]+://", "postgresql://", url)
    url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _reset_public_schema(psycopg_uri: str) -> None:
    with psycopg.connect(psycopg_uri, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS public CASCADE;")
            cur.execute("CREATE SCHEMA public;")
            cur.execute("GRANT ALL ON SCHEMA public TO CURRENT_USER;")
            cur.execute("GRANT ALL ON SCHEMA public TO public;")


def _alembic_config(sqlalchemy_url: str) -> Config:
    cfg = Config("alembic.ini")
    configuration = (
        ("script_location", "src/shortener_app/infrastructures/db/migrations"),
        ("sqlalchemy.url", sqlalchemy_url),
    )

    [cfg.set_main_option(name, value) for name, value in configuration]

    return cfg


@pytest.fixture(scope="session")
def pg_container() -> Generator[PostgresContainer, Any]:
    with PostgresContainer("postgres:16") as pg:
        yield pg


@pytest.fixture
def alembic_cfg(pg_container: PostgresContainer) -> Config:
    raw_url = pg_container.get_connection_url()

    psycopg_uri = _to_psycopg_uri(raw_url)
    sqlalchemy_url = _to_sqlalchemy_url(raw_url)

    _reset_public_schema(psycopg_uri)
    return _alembic_config(sqlalchemy_url)


@pytest.fixture(scope="session")
def alembic_cfg_nodb() -> Config:
    cfg = Config("alembic.ini")
    configuration = (
        ("script_location", "src/shortener_app/infrastructures/db/migrations"),
        ("sqlalchemy.url", "postgresql+psycopg://user:pass@localhost/dbname"),
    )

    [cfg.set_main_option(name, value) for name, value in configuration]

    return cfg
