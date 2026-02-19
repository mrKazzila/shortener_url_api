__all__ = ("get_providers",)

from typing import TYPE_CHECKING

from shortener_app.config.ioc.bundles import (
    CONSUMER_PROVIDERS as _CONSUMER_PROVIDERS,
    GRPC_PROVIDERS as _GRPC_PROVIDERS,
)

if TYPE_CHECKING:
    from dishka import Provider


def get_providers(*, is_consumer: bool = False) -> tuple["Provider", ...]:
    return _CONSUMER_PROVIDERS if is_consumer else _GRPC_PROVIDERS
