from typing import final

from pydantic import Field

from shortener_app.config.settings._base_settings import BaseAppSettings


@final
class DatabaseSettings(BaseAppSettings):
    database_dsn: str = Field(..., validation_alias="DATABASE_DSN")
