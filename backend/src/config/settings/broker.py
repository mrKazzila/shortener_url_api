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
    broker_new_artifact_queue: str = Field(
        "new_urls",
        validation_alias="BROKER_NEW_ARTIFACT_QUEUE",
    )

    publish_retries: int = Field(3, validation_alias="PUBLISH_RETRIES")
    publish_retry_backoff: float = Field(
        0.5,
        validation_alias="PUBLISH_RETRY_BACKOFF",
    )

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3].joinpath("env/.env"),
        extra="allow",
    )
