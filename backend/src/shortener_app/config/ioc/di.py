__all__ = ("get_providers",)

from dishka import Provider

from shortener_app.config.ioc.consumer_providers import CONSUMER_PROVIDERS
from shortener_app.config.ioc.providers import PROVIDERS


def get_providers(is_consumer: bool = False) -> list[Provider]:
    return CONSUMER_PROVIDERS if is_consumer else PROVIDERS
