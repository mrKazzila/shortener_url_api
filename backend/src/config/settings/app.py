from pathlib import Path
from typing import Literal, final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


@final
class AppSettings(BaseSettings):
    environment: Literal["local", "dev", "development", "prod"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    debug: bool = Field(False, validation_alias="DEBUG")

    key_length: int = Field(5, validation_alias="KEY_LENGTH")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3].joinpath("env/.env"),
        extra="allow",
    )
