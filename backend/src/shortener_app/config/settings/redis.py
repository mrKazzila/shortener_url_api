from typing import final

from pydantic import Field, RedisDsn

from shortener_app.config.settings._base_settings import BaseAppSettings


@final
class RedisSettings(BaseAppSettings):
    redis_dsn: RedisDsn = Field(..., validation_alias="REDIS_DSN")

    redis_cache_ttl: int = Field(3600, validation_alias="REDIS_CACHE_TTL")
    redis_cache_prefix: str = Field(
        "short:",
        validation_alias="REDIS_CACHE_PREFIX",
    )
