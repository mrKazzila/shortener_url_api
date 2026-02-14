import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory


@pytest.mark.migrations
def test_migrations_have_single_head(alembic_cfg_nodb: Config) -> None:
    script = ScriptDirectory.from_config(alembic_cfg_nodb)

    heads = script.get_heads()

    assert len(heads) == 1, f"Expected 1 head, got {len(heads)}: {heads}"


@pytest.mark.migrations
def test_migrations_apply_to_empty_db(alembic_cfg: Config) -> None:
    command.upgrade(alembic_cfg, "head")


@pytest.mark.migrations
def test_schema_matches_models_after_upgrade(alembic_cfg: Config) -> None:
    command.upgrade(alembic_cfg, "head")

    command.check(alembic_cfg)


@pytest.mark.migrations
def test_migrations_roundtrip_base_to_head(alembic_cfg: Config) -> None:
    command.upgrade(alembic_cfg, "head")
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")

    command.check(alembic_cfg)
