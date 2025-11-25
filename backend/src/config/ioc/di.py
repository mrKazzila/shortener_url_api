from functools import lru_cache

from dishka import Provider

from src.config.ioc.consumer_providers import CONSUMER_PROVIDERS
from src.config.ioc.providers import PROVIDERS


@lru_cache
def get_providers(is_consumer: bool = False) -> list[Provider]:
    """
    Returns a list of Dishka providers for dependency injection.

    Returns:
        list[Provider]: A list of configured providers.
    """
    return CONSUMER_PROVIDERS if is_consumer else PROVIDERS
