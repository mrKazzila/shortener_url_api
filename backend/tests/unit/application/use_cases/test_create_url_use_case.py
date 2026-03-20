from typing import cast
from uuid import uuid4

import pytest

from shortener_app.application.dtos.urls.urls_cache import UrlCacheSeedDTO
from shortener_app.application.dtos.urls.urls_events import PublishUrlDTO
from shortener_app.application.dtos.urls.urls_requests import CreateUrlDTO
from shortener_app.application.dtos.urls.urls_responses import CreatedUrlDTO
from shortener_app.application.mappers.url_dto_facade import UrlDtoFacade
from shortener_app.application.use_cases.create_short_url import (
    CreateUrlUseCase,
)
from shortener_app.application.use_cases.internal.create_uniq_key_in_cache import (
    CreateUniqKeyUseCase,
)
from tests.testkit.internal_uc import FakeCreateUniqKeyUseCase
from tests.testkit.publish_queue import SpyNewUrlPublishQueue
from tests.testkit.url_facade import SpyUrlDtoFacade

pytestmark = pytest.mark.unit


def make_create_dto(
    *,
    target_url: str = "https://example.com",
) -> CreateUrlDTO:
    return CreateUrlDTO(
        target_url=target_url,
        user_id=uuid4(),
    )


@pytest.mark.asyncio
async def test_execute_happy_path_generates_key_publishes_and_returns_created_dto() -> (
    None
):
    dto = make_create_dto(target_url="https://example.com")

    key_uc = FakeCreateUniqKeyUseCase(return_key="Ab12Z")

    publish_dto = PublishUrlDTO(
        key="Ab12Z",
        target_url=dto.target_url,
        user_id=dto.user_id,
    )
    created_dto = CreatedUrlDTO(
        key="Ab12Z",
        target_url=dto.target_url,
        user_id=dto.user_id,
    )

    mapper = SpyUrlDtoFacade(
        return_publish_dto=publish_dto,
        return_created_dto=created_dto,
    )

    queue = SpyNewUrlPublishQueue()

    uc = CreateUrlUseCase(
        create_uniq_key_uc=cast(CreateUniqKeyUseCase, key_uc),
        publish_url_queue=queue,
        mapper=cast(UrlDtoFacade, mapper),
    )

    result = await uc.execute(dto=dto)

    # 1) key uc вызван один раз с правильным seed
    assert len(key_uc.calls) == 1
    assert key_uc.calls[0] == UrlCacheSeedDTO(
        target_url=dto.target_url,
        user_id=dto.user_id,
        name=None,
        is_active=True,
    )

    assert len(mapper.to_publish_calls) == 1
    entity_for_publish = mapper.to_publish_calls[0]
    assert entity_for_publish.id == 0
    assert entity_for_publish.key == "Ab12Z"
    assert entity_for_publish.target_url == dto.target_url
    assert entity_for_publish.user_id == dto.user_id

    assert queue.calls == [publish_dto]

    assert len(mapper.to_created_calls) == 1
    entity_for_created = mapper.to_created_calls[0]
    assert entity_for_created.key == "Ab12Z"
    assert result == created_dto


@pytest.mark.asyncio
async def test_execute_does_not_enqueue_if_key_generation_fails() -> None:
    dto = make_create_dto()

    key_uc = FakeCreateUniqKeyUseCase(exc=RuntimeError("keygen down"))

    mapper = SpyUrlDtoFacade(
        return_publish_dto=PublishUrlDTO(
            key="xxxxx",
            target_url=dto.target_url,
            user_id=dto.user_id,
        ),
        return_created_dto=CreatedUrlDTO(
            key="xxxxx",
            target_url=dto.target_url,
            user_id=dto.user_id,
        ),
    )

    queue = SpyNewUrlPublishQueue()

    uc = CreateUrlUseCase(
        create_uniq_key_uc=cast(CreateUniqKeyUseCase, key_uc),
        publish_url_queue=queue,
        mapper=cast(UrlDtoFacade, mapper),
    )

    with pytest.raises(RuntimeError, match="keygen down"):
        await uc.execute(dto=dto)

    assert len(key_uc.calls) == 1
    assert queue.calls == []
    assert mapper.to_publish_calls == []
    assert mapper.to_created_calls == []


@pytest.mark.asyncio
async def test_execute_propagates_queue_error_and_does_not_build_created_dto() -> (
    None
):
    dto = make_create_dto()

    key_uc = FakeCreateUniqKeyUseCase(return_key="Ab12Z")

    publish_dto = PublishUrlDTO(
        key="Ab12Z",
        target_url=dto.target_url,
        user_id=dto.user_id,
    )
    created_dto = CreatedUrlDTO(
        key="Ab12Z",
        target_url=dto.target_url,
        user_id=dto.user_id,
    )

    mapper = SpyUrlDtoFacade(
        return_publish_dto=publish_dto,
        return_created_dto=created_dto,
    )
    queue = SpyNewUrlPublishQueue(exc=RuntimeError("queue down"))

    uc = CreateUrlUseCase(
        create_uniq_key_uc=cast(CreateUniqKeyUseCase, key_uc),
        publish_url_queue=queue,
        mapper=cast(UrlDtoFacade, mapper),
    )

    with pytest.raises(RuntimeError, match="queue down"):
        await uc.execute(dto=dto)

    assert len(mapper.to_publish_calls) == 1
    assert queue.calls == [publish_dto]

    assert mapper.to_created_calls == []
