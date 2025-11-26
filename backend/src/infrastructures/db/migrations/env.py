from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.config.settings.loader import get_settings
from src.infrastructures.db.models import Base

settings = get_settings()


config = context.config
config.set_main_option(
    "sqlalchemy.url",
    f"{settings.sqlalchemy_database_uri}?async_fallback=True",
)

_sqlalchemy_url = config.get_main_option("sqlalchemy.url")

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


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
    context.configure(
        url=_sqlalchemy_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    config_section = config.get_section(config.config_ini_section, {})
    config_section["sqlalchemy.url"] = _sqlalchemy_url

    connectable = engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
