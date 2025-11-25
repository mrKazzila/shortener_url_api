from typing import final

from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


@final
class RedisSettings(BaseSettings):
    redis_url: RedisDsn = Field(
        RedisDsn("redis://:redis_password@redis:6379/0"), validation_alias="REDIS_URL"
    )
    redis_password: str = Field("redis_password", validation_alias="REDIS_PASSWORD")
    redis_host: str = Field("redis", validation_alias="REDIS_HOST")
    redis_port: int = Field(6379, validation_alias="REDIS_PORT")
    redis_db: int = Field(0, validation_alias="REDIS_DB")
    redis_cache_ttl: int = Field(3600, validation_alias="REDIS_CACHE_TTL")
    redis_cache_prefix: str = Field("antiques:", validation_alias="REDIS_CACHE_PREFIX")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3].joinpath("env/.env"),
        extra="allow",
    )
