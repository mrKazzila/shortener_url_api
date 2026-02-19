__all__ = ("get_consumer_providers",)

from dishka import Provider

from shortener_app.config.ioc.bundles.common import COMMON_PROVIDERS
from shortener_app.config.ioc.bundles.consumer import CONSUMER_ONLY_PROVIDERS


def get_consumer_providers() -> tuple[Provider, ...]:
    return *COMMON_PROVIDERS, *CONSUMER_ONLY_PROVIDERS
