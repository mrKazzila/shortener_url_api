__all__ = ("BaseAppSettings",)

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
def _env_file_path() -> Path:
    return Path(__file__).resolve().parents[3].joinpath("env/.env")


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_file_path(),
        extra="allow",
    )
