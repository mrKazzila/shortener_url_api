from pathlib import Path
from typing import final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


@final
class BrokerSettings(BaseSettings):
    broker_url: str = Field(
        ...,
        validation_alias="BROKER_URL",
    )

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3].joinpath("env/.env"),
        extra="allow",
    )
