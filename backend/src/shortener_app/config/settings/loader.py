__all__ = ("get_settings",)

from functools import lru_cache

from shortener_app.config.settings.base import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()
