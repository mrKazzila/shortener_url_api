__all__ = ("get_providers",)

from dishka import Provider

from src.config.ioc.consumer_providers import CONSUMER_PROVIDERS
from src.config.ioc.providers import PROVIDERS


def get_providers(is_consumer: bool = False) -> list[Provider]:
    return CONSUMER_PROVIDERS if is_consumer else PROVIDERS
