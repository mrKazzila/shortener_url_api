import re

import pytest

from shortener_app.domain.services.key_generator import RandomKeyGenerator

pytestmark = pytest.mark.unit


def test_default_length_is_5() -> None:
    gen = RandomKeyGenerator()

    key = gen()

    assert isinstance(key, str)
    assert len(key) == 5


def test_custom_length() -> None:
    gen = RandomKeyGenerator(length=10)

    key = gen()

    assert len(key) == 10


def test_uses_only_declared_chars() -> None:
    gen = RandomKeyGenerator(length=50)
    key = gen()

    allowed = re.escape(gen.chars)
    assert re.fullmatch(rf"[{allowed}]+", key)


def test_reasonable_uniqueness() -> None:
    gen = RandomKeyGenerator()
    keys = [gen() for _ in range(500)]
    assert len(set(keys)) == len(keys)
