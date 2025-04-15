import logging
from pathlib import Path
from sys import exit
from typing import Annotated, Literal, cast

from annotated_types import Ge, Le, MinLen
from pydantic import PostgresDsn, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("settings", "Settings")

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Main settings for project."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2].joinpath("env/.env"),
    )

    POSTGRES_VERSION: str

    DB_PROTOCOL: str
    DB_HOST: str
    DB_PORT: cast(str, Annotated[int, Ge(1), Le(65_535)])
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: Annotated[SecretStr, MinLen(8)]

    @property
    def dsn(self, protocol=None) -> PostgresDsn:
        protocol = protocol or self.DB_PROTOCOL

        return PostgresDsn.build(
            scheme=protocol,
            username=self.DB_USER,
            password=self.DB_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=f"{self.DB_NAME}",
        )

    APP_NAME: str
    APP_VERSION: str
    MODE: Literal["TEST", "DEV", "PROD"]

    BASE_URL: str
    DOMAIN: str
    DOMAIN_PORT: Annotated[int, Ge(1), Le(65_535)]

    KEY_LENGTH: Annotated[int, Ge(3), Le(10)]

    USER_HEADER: str


def get_settings() -> Settings | None:
    logger.info("Loading settings from env")

    try:
        return Settings()

    except ValidationError as error_:
        logger.error("Error at loading settings from env. %s", error_)
        exit(str(error_))


settings = get_settings()
