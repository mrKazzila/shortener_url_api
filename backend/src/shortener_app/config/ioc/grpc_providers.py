__all__ = ("get_grpc_providers",)

from dishka import Provider

from shortener_app.config.ioc.bundles.common import COMMON_PROVIDERS
from shortener_app.config.ioc.bundles.grpc import GRPC_ONLY_PROVIDERS


def get_grpc_providers() -> tuple[Provider, ...]:
    return *COMMON_PROVIDERS, *GRPC_ONLY_PROVIDERS
