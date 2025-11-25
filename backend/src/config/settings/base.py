from typing import final

from pydantic import Field
from pydantic_settings import BaseSettings

from src.config.settings.app import AppSettings
from src.config.settings.broker import BrokerSettings
from src.config.settings.cors import CORSSettings
from src.config.settings.database import DatabaseSettings
from src.config.settings.redis import RedisSettings


@final
class Settings(BaseSettings):
    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    broker: BrokerSettings = Field(default_factory=BrokerSettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)

    @property
    def app_name(self) -> str:
        return self.app.app_name

    @property
    def user_header(self) -> str:
        return self.app.user_header

    @property
    def app_version(self) -> str:
        return self.app.app_version

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
    def sqlalchemy_database_uri(self) -> str:
        return str(self.database.sqlalchemy_database_uri)

    @property
    def redis_url(self) -> str:
        return str(self.redis.redis_url)

    @property
    def catalog_api_base(self) -> str:
        return self.external_apis.catalog_api_base

    @property
    def http_timeout(self) -> float:
        return self.external_apis.http_timeout

    @property
    def broker_url(self) -> str:
        return self.broker.broker_url

    @property
    def broker_new_artifact_queue(self) -> str:
        return self.broker.broker_new_artifact_queue

    @property
    def publish_retries(self) -> int:
        return self.broker.publish_retries

    @property
    def publish_retry_backoff(self) -> float:
        return self.broker.publish_retry_backoff

    @property
    def redis_password(self) -> str:
        return self.redis.redis_password

    @property
    def redis_port(self) -> int:
        return self.redis.redis_port

    @property
    def redis_host(self) -> str:
        return self.redis.redis_host

    @property
    def redis_db(self) -> int:
        return self.redis.redis_db

    @property
    def redis_cache_ttl(self) -> int:
        return self.redis.redis_cache_ttl

    @property
    def redis_cache_prefix(self) -> str:
        return self.redis.redis_cache_prefix

    @property
    def cors_origins(self) -> list[str]:
        return self.cors.cors_origins

    @property
    def cors_allow_credentials(self) -> bool:
        return self.cors.cors_allow_credentials

    @property
    def cors_allow_methods(self) -> list[str]:
        return self.cors.cors_allow_methods

    @property
    def cors_allow_headers(self) -> list[str]:
        return self.cors.cors_allow_headers

    @property
    def postgres_user(self) -> str:
        return self.database.postgres_user

    @property
    def postgres_password(self) -> str:
        return self.database.postgres_password

    @property
    def postgres_server(self) -> str:
        return self.database.postgres_server

    @property
    def postgres_port(self) -> int:
        return self.database.postgres_port

    @property
    def postgres_db(self) -> str:
        return self.database.postgres_db
