from typing import cast, final

from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


@final
class DatabaseSettings(BaseSettings):
    postgres_protocol: str = Field(..., validation_alias="DB_PROTOCOL")
    postgres_user: str = Field(..., validation_alias="DB_USER")
    postgres_password: str = Field(..., validation_alias="DB_PASSWORD")
    postgres_server: str = Field(..., validation_alias="DB_HOST")
    postgres_port: int = Field(5432, validation_alias="DB_PORT")
    postgres_db: str = Field(..., validation_alias="DB_NAME")

    @computed_field
    def database_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=self.postgres_protocol,
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_server,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    @computed_field
    def sqlalchemy_database_uri(self) -> PostgresDsn:
        return cast("PostgresDsn", self.database_url)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3].joinpath("env/.env"),
        extra="allow",
    )