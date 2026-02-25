from __future__ import annotations

from uuid import uuid4

import pytest

from shortener_app.domain.entities.url import UrlEntity
from shortener_app.infrastructures.db.mappers.url_db_mapper import UrlDBMapper
from shortener_app.infrastructures.db.repository import SQLAlchemyRepository
from shortener_app.infrastructures.db.uow import UnitOfWork

pytestmark = pytest.mark.integration


def _make_repo_and_uow(session):
    mapper = UrlDBMapper()
    repo = SQLAlchemyRepository(mapper=mapper, session=session)
    uow = UnitOfWork(session=session, repository=repo)
    return repo, uow


@pytest.mark.asyncio
async def test_add_bulk_and_get_by_key(session) -> None:
    repo, uow = _make_repo_and_uow(session)

    entity = UrlEntity.create(
        user_id=uuid4(),
        target_url="https://example.com",
        key="Ab12Z",
        name=None,
    )

    async with uow:
        await repo.add_bulk(entities=[entity])

    found = await repo.get(reference={"key": "Ab12Z"})
    assert found is not None
    assert found.key == "Ab12Z"
    assert found.target_url == "https://example.com"
    assert found.user_id == entity.user_id


@pytest.mark.asyncio
async def test_update_changes_name_and_is_active(session) -> None:
    repo, uow = _make_repo_and_uow(session)

    entity = UrlEntity.create(
        user_id=uuid4(),
        target_url="https://example.com",
        key="Ab12Z",
        name=None,
    )

    async with uow:
        await repo.add_bulk(entities=[entity])

    updated = entity.update(name="new-name", is_active=False)

    async with uow:
        await repo.update(entity=updated)

    found = await repo.get(reference={"key": "Ab12Z"})
    assert found is not None
    assert found.name == "new-name"
    assert found.is_active is False
    assert found.target_url == "https://example.com"
    assert found.user_id == entity.user_id


@pytest.mark.asyncio
async def test_delete_removes_row(session) -> None:
    repo, uow = _make_repo_and_uow(session)

    entity = UrlEntity.create(
        user_id=uuid4(),
        target_url="https://example.com",
        key="Ab12Z",
        name=None,
    )

    async with uow:
        await repo.add_bulk(entities=[entity])

    async with uow:
        await repo.delete(entity=entity)

    found = await repo.get(reference={"key": "Ab12Z"})
    assert found is None


@pytest.mark.asyncio
async def test_apply_click_events_increments_clicks_count(session) -> None:
    repo, uow = _make_repo_and_uow(session)

    key = "Ab12Z"
    entity = UrlEntity.create(
        user_id=uuid4(),
        target_url="https://example.com",
        key=key,
        name=None,
    )

    async with uow:
        await repo.add_bulk(entities=[entity])

    e1 = uuid4()
    e2 = uuid4()

    async with uow:
        inserted = await repo.apply_click_events(events=[(e1, key), (e2, key)])
        assert inserted == 2

    found = await repo.get(reference={"key": key})
    assert found is not None
    assert found.clicks_count == 2


@pytest.mark.asyncio
async def test_apply_click_events_ignores_duplicate_event_id(session) -> None:
    repo, uow = _make_repo_and_uow(session)

    key = "Ab12Z"
    entity = UrlEntity.create(
        user_id=uuid4(),
        target_url="https://example.com",
        key=key,
        name=None,
    )

    async with uow:
        await repo.add_bulk(entities=[entity])

    event_id = uuid4()

    async with uow:
        inserted = await repo.apply_click_events(
            events=[(event_id, key), (event_id, key)],
        )
        assert inserted == 1

    found = await repo.get(reference={"key": key})
    assert found is not None
    assert found.clicks_count == 1
