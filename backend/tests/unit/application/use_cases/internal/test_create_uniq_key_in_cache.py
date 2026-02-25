from typing import cast
from uuid import uuid4

import pytest

from shortener_app.application.dtos.urls.urls_cache import (
    UrlCacheRecordDTO,
    UrlCacheSeedDTO,
)
from shortener_app.application.use_cases.internal.create_uniq_key_in_cache import (
    CreateUniqKeyUseCase,
)
from shortener_app.domain.services.key_generator import RandomKeyGenerator
from tests.testkit.cache import FakeCache
from tests.testkit.codec import SpyDtoCodec
from tests.testkit.keygen import SequenceKeyGenerator

pytestmark = pytest.mark.unit


def make_seed(
    *,
    target_url: str = "https://example.com",
    name: str | None = None,
    is_active: bool = True,
) -> UrlCacheSeedDTO:
    return UrlCacheSeedDTO(
        target_url=target_url,
        user_id=uuid4(),
        name=name,
        is_active=is_active,
    )


@pytest.mark.asyncio
async def test_returns_key_when_cache_set_nx_succeeds_first_try() -> None:
    seed = make_seed(name="my-url", is_active=True)

    keygen = SequenceKeyGenerator(keys=["Ab12Z"])
    cache = FakeCache(set_nx_results=[True])
    codec = SpyDtoCodec(return_value={"encoded": "ok"})

    uc = CreateUniqKeyUseCase(
        key_generator=cast(RandomKeyGenerator, keygen),
        cache=cache,
        codec=codec,
        ttl_seconds=123,
        max_attempts=50,
    )

    key = await uc.execute(seed=seed)

    assert key == "Ab12Z"
    assert keygen.calls == 1

    assert len(codec.encode_calls) == 1
    record = codec.encode_calls[0]
    assert isinstance(record, UrlCacheRecordDTO)

    assert record.key == "Ab12Z"
    assert record.target_url == seed.target_url
    assert record.user_id == seed.user_id
    assert record.name == seed.name
    assert record.is_active == seed.is_active

    assert cache.set_nx_calls == [("short:Ab12Z", {"encoded": "ok"}, 123)]


@pytest.mark.asyncio
async def test_retries_on_collisions_until_success() -> None:
    seed = make_seed()

    keygen = SequenceKeyGenerator(keys=["AAAAA", "BBBBB", "CCCCC"])
    cache = FakeCache(set_nx_results=[False, False, True])
    codec = SpyDtoCodec(return_value="blob")

    uc = CreateUniqKeyUseCase(
        key_generator=cast(RandomKeyGenerator, keygen),
        cache=cache,
        codec=codec,
        ttl_seconds=None,
        max_attempts=50,
    )

    key = await uc.execute(seed=seed)

    assert key == "CCCCC"
    assert keygen.calls == 3

    assert [k for (k, _v, _ttl) in cache.set_nx_calls] == [
        "short:AAAAA",
        "short:BBBBB",
        "short:CCCCC",
    ]
    assert cache.set_nx_calls[-1] == ("short:CCCCC", "blob", None)

    assert len(codec.encode_calls) == 3


@pytest.mark.asyncio
async def test_raises_after_max_attempts_exceeded() -> None:
    seed = make_seed()

    keygen = SequenceKeyGenerator(keys=["ZZZZZ"])
    cache = FakeCache(set_nx_results=[False])
    codec = SpyDtoCodec(return_value={"x": 1})

    uc = CreateUniqKeyUseCase(
        key_generator=cast(RandomKeyGenerator, keygen),
        cache=cache,
        codec=codec,
        max_attempts=3,
    )

    with pytest.raises(RuntimeError, match="Failed to allocate unique key"):
        await uc.execute(seed=seed)

    assert keygen.calls == 3
    assert len(cache.set_nx_calls) == 3
    assert len(codec.encode_calls) == 3
