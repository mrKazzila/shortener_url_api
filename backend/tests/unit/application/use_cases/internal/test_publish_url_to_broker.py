from uuid import uuid4

import pytest

from shortener_app.application.dtos.urls.urls_events import PublishUrlDTO
from shortener_app.application.use_cases.internal.publish_data_to_broker import (
    PublishUrlToBrokerUseCase,
)
from tests.testkit.broker import FakeMessageBrokerPublisher

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_execute_batch_calls_broker_with_same_dtos_list() -> None:
    broker = FakeMessageBrokerPublisher()
    uc = PublishUrlToBrokerUseCase(message_broker=broker)

    dtos = [
        PublishUrlDTO(
            key="Ab12Z",
            target_url="https://a.example",
            user_id=uuid4(),
        ),
        PublishUrlDTO(
            key="Qw34E",
            target_url="https://b.example",
            user_id=uuid4(),
        ),
    ]

    await uc.execute_batch(dtos=dtos)

    assert broker.publish_new_urls_batch_calls == [dtos]
    assert broker.publish_update_url_calls == []


@pytest.mark.asyncio
async def test_execute_batch_propagates_broker_error() -> None:
    broker = FakeMessageBrokerPublisher(
        raise_on_publish_new_urls_batch=RuntimeError("broker down"),
    )
    uc = PublishUrlToBrokerUseCase(message_broker=broker)

    dtos = [
        PublishUrlDTO(
            key="Ab12Z",
            target_url="https://a.example",
            user_id=uuid4(),
        ),
    ]

    with pytest.raises(RuntimeError, match="broker down"):
        await uc.execute_batch(dtos=dtos)

    assert broker.publish_new_urls_batch_calls == [dtos]
