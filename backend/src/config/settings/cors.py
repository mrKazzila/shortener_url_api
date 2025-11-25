from typing import final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


@final
class CORSSettings(BaseSettings):
    cors_origins: list[str] = Field(
        ["http://localhost:3000", "http://localhost:8080"], validation_alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(True, validation_alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: list[str] = Field(
        ["GET", "POST", "PUT", "DELETE", "OPTIONS"], validation_alias="CORS_ALLOW_METHODS"
    )
    cors_allow_headers: list[str] = Field(["*"], validation_alias="CORS_ALLOW_HEADERS")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3].joinpath("env/.env"),
        extra="allow",
    )
