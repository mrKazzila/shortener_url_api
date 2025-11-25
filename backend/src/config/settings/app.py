from typing import Literal, final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


@final
class AppSettings(BaseSettings):
    """
    Application core settings.

    Attributes:
        app_name (str): Name of the application.
        environment (Literal["local", "dev", "development", "prod"]): Application environment.
        log_level (Literal["DEBUG", "INFO", "WARNING", "ERROR"]): Logging level.
        debug (bool): Debug mode flag.
    """

    app_name: str = "ShortenerApi"
    app_version: str = Field(..., validation_alias="APP_VERSION")
    description: str = "Simple API for url shortener logic"

    environment: Literal["local", "dev", "development", "prod"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    debug: bool = Field(False, validation_alias="DEBUG")

    key_length: int = Field(5, validation_alias="KEY_LENGTH")

    user_header: str = Field("X-User-ID", validation_alias="USER_HEADER")


    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3].joinpath("env/.env"),
        extra="allow",
    )
