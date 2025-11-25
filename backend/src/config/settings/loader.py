from functools import lru_cache

from src.config.settings.base import Settings

__all__ = ("get_settings",)


@lru_cache
def get_settings() -> Settings:
    return Settings()
