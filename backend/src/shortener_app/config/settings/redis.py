from typing import final

from pydantic import Field, RedisDsn, computed_field

from shortener_app.config.settings._base_settings import BaseAppSettings


@final
class RedisSettings(BaseAppSettings):
    redis_password: str = Field(
        "redis_password",
        validation_alias="REDIS_PASSWORD",
    )
    redis_user: str | None = Field(
        default=None,
        validation_alias="REDIS_USER",
    )
    redis_host: str = Field("redis", validation_alias="REDIS_HOST")
    redis_port: int = Field(6379, validation_alias="REDIS_PORT")
    redis_db: int = Field(0, validation_alias="REDIS_DB")

    redis_cache_ttl: int = Field(3600, validation_alias="REDIS_CACHE_TTL")
    redis_cache_prefix: str = Field(
        "short:",
        validation_alias="REDIS_CACHE_PREFIX",
    )

    @computed_field
    def redis_url(self) -> RedisDsn:
        t = RedisDsn.build(
            scheme="redis",
            username=self.redis_user,
            password=self.redis_password,
            host=self.redis_host,
            port=self.redis_port,
            path=f"/{self.redis_db}",
        )

        print(f"REDIS: {t=!r}")
        return RedisDsn.build(
            scheme="redis",
            username=self.redis_user,
            password=self.redis_password,
            host=self.redis_host,
            port=self.redis_port,
            path=f"/{self.redis_db}",
        )
