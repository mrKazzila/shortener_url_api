from typing import final

from pydantic import Field

from shortener_app.config.settings._base_settings import BaseAppSettings
from shortener_app.config.settings.app import AppSettings
from shortener_app.config.settings.broker import BrokerSettings
from shortener_app.config.settings.database import DatabaseSettings
from shortener_app.config.settings.redis import RedisSettings


@final
class Settings(BaseAppSettings):
    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    broker: BrokerSettings = Field(default_factory=BrokerSettings)

    @property
    def environment(self) -> str:
        return self.app.environment

    @property
    def log_level(self) -> str:
        return self.app.log_level

    @property
    def debug(self) -> bool:
        return self.app.debug

    @property
    def database_url(self) -> str:
        return str(self.database.database_url)

    @property
    def redis_url(self) -> str:
        return str(self.redis.redis_url)

    @property
    def redis_cache_ttl(self) -> int:
        return self.redis.redis_cache_ttl

    @property
    def redis_cache_prefix(self) -> str:
        return self.redis.redis_cache_prefix

    @property
    def broker_url(self) -> str:
        return self.broker.broker_url
