from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from shortener_app.domain.entities.url import UrlEntity
from shortener_app.domain.exceptions.domain import ValidationError

pytestmark = pytest.mark.unit


def test_create_sets_defaults() -> None:
    user_id = uuid4()

    e = UrlEntity.create(
        user_id=user_id,
        target_url="https://example.com",
        key="Ab12Z",
        name=None,
    )

    assert e.id == 0
    assert e.user_id == user_id
    assert e.target_url == "https://example.com"
    assert e.key == "Ab12Z"
    assert e.name is None

    assert e.is_active is True
    assert e.clicks_count == 0

    assert isinstance(e.created_at, datetime)
    assert isinstance(e.last_used, datetime)
    assert e.created_at.tzinfo is not None
    assert e.last_used >= e.created_at


def test_update_changes_only_specified_fields() -> None:
    user_id = uuid4()

    e1 = UrlEntity.create(
        user_id=user_id,
        target_url="https://example.com",
        key="Ab12Z",
        name=None,
    )
    e2 = e1.update(name="my link")

    assert e2 is not e1
    assert e2.name == "my link"
    assert e2.is_active == e1.is_active
    assert e2.last_used == e1.last_used


def test_update_can_toggle_is_active() -> None:
    e1 = UrlEntity.create(
        user_id=uuid4(),
        target_url="https://example.com",
        key="Ab12Z",
    )
    e2 = e1.update(is_active=False)

    assert e2.is_active is False
    assert e1.is_active is True


def test_update_touch_last_used_updates_timestamp() -> None:
    e1 = UrlEntity.create(
        user_id=uuid4(),
        target_url="https://example.com",
        key="Ab12Z",
    )
    old = e1.last_used
    e2 = e1.update(touch_last_used=True)

    assert e2.last_used >= old
    assert e2.created_at == e1.created_at


def test_validation_key_must_be_exactly_5_chars() -> None:
    with pytest.raises(ValidationError):
        UrlEntity.create(
            user_id=uuid4(),
            target_url="https://example.com",
            key="1234",  # 4
        )

    with pytest.raises(ValidationError):
        UrlEntity.create(
            user_id=uuid4(),
            target_url="https://example.com",
            key="123456",  # 6
        )


def test_validation_last_used_cannot_be_earlier_than_created_at() -> None:
    now = datetime.now(UTC)
    created_at = now
    last_used = now - timedelta(seconds=1)

    with pytest.raises(ValidationError):
        UrlEntity(
            id=1,
            user_id=uuid4(),
            key="Ab12Z",
            target_url="https://example.com",
            created_at=created_at,
            last_used=last_used,
        )


def test_validation_created_at_cannot_be_in_future() -> None:
    future = datetime.now(UTC) + timedelta(days=1)

    with pytest.raises(ValidationError):
        UrlEntity(
            id=1,
            user_id=uuid4(),
            key="Ab12Z",
            target_url="https://example.com",
            created_at=future,
            last_used=future,
        )


def test_validation_clicks_count_cannot_be_negative() -> None:
    with pytest.raises(ValidationError):
        UrlEntity(
            id=1,
            user_id=uuid4(),
            key="Ab12Z",
            target_url="https://example.com",
            clicks_count=-1,
        )
