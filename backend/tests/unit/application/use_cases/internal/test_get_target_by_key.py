from typing import cast
from uuid import uuid4

import pytest

from shortener_app.application.dtos.urls.urls_cache import UrlCacheRecordDTO
from shortener_app.application.mappers.url_dto_facade import UrlDtoFacade
from shortener_app.application.use_cases.internal.get_target_url_by_key import (
    GetTargetByKeyUseCase,
)
from shortener_app.domain.entities.url import UrlEntity
from tests.testkit.cache import FakeCache
from tests.testkit.codec import SpyDtoCodec
from tests.testkit.repository import FakeRepository
from tests.testkit.uow import FakeUnitOfWork
from tests.testkit.url_facade import SpyUrlDtoFacade

pytestmark = pytest.mark.unit


def make_entity(*, key: str, target_url: str) -> UrlEntity:
    return UrlEntity.create(
        user_id=uuid4(),
        target_url=target_url,
        key=key,
        name=None,
    )


@pytest.mark.asyncio
async def test_cache_hit_decodes_maps_and_skips_db() -> None:
    key = "Ab12Z"

    cache_value = {"raw": "from-redis"}
    cache = FakeCache()
    cache.store[f"short:{key}"] = cache_value

    cache_dto = UrlCacheRecordDTO(
        key=key,
        target_url="https://cached.example",
        user_id=uuid4(),
        name="from-cache",
        is_active=True,
    )

    codec = SpyDtoCodec(return_value={"ignored": "x"})
    codec.decode_value = cache_dto

    mapped_entity = make_entity(key=key, target_url=cache_dto.target_url)
    mapper_spy = SpyUrlDtoFacade(return_entity=mapped_entity)

    repo = FakeRepository(
        get_result=make_entity(key=key, target_url="https://db.example"),
    )
    uow = FakeUnitOfWork(repository=repo)

    uc = GetTargetByKeyUseCase(
        cache=cache,
        uow=uow,
        mapper=cast(UrlDtoFacade, mapper_spy),
        codec=codec,
    )

    result = await uc.execute(key=key)

    assert result == mapped_entity
    assert cache.get_calls == [f"short:{key}"]
    assert codec.decode_calls == [cache_value]
    assert mapper_spy.to_entity_from_cache_calls == [cache_dto]
    assert repo.get_calls == []


@pytest.mark.asyncio
async def test_cache_miss_fetches_from_repository() -> None:
    key = "Ab12Z"

    cache = FakeCache()
    codec = SpyDtoCodec(return_value={"ignored": "x"})

    mapper_spy = SpyUrlDtoFacade(
        return_entity=make_entity(
            key=key,
            target_url="https://mapped.example",
        ),
    )

    db_entity = make_entity(key=key, target_url="https://db.example")
    repo = FakeRepository(get_result=db_entity)
    uow = FakeUnitOfWork(repository=repo)

    uc = GetTargetByKeyUseCase(
        cache=cache,
        uow=uow,
        mapper=cast(UrlDtoFacade, mapper_spy),
        codec=codec,
    )

    result = await uc.execute(key=key)

    assert result == db_entity
    assert cache.get_calls == [f"short:{key}"]
    assert codec.decode_calls == []
    assert mapper_spy.to_entity_from_cache_calls == []
    assert repo.get_calls == [{"key": key}]


@pytest.mark.asyncio
async def test_cache_miss_returns_none_when_repo_returns_none() -> None:
    key = "Ab12Z"

    cache = FakeCache()
    codec = SpyDtoCodec(return_value={"ignored": "x"})
    mapper_spy = SpyUrlDtoFacade(
        return_entity=make_entity(
            key=key,
            target_url="https://mapped.example",
        ),
    )

    repo = FakeRepository(get_result=None)
    uow = FakeUnitOfWork(repository=repo)

    uc = GetTargetByKeyUseCase(
        cache=cache,
        uow=uow,
        mapper=cast(UrlDtoFacade, mapper_spy),
        codec=codec,
    )

    result = await uc.execute(key=key)

    assert result is None
    assert cache.get_calls == [f"short:{key}"]
    assert repo.get_calls == [{"key": key}]
    assert codec.decode_calls == []
    assert mapper_spy.to_entity_from_cache_calls == []
