from typing import Literal, final

from pydantic import Field

from shortener_app.config.settings._base_settings import BaseAppSettings


@final
class AppSettings(BaseAppSettings):
    environment: Literal["local", "dev", "development", "prod"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    debug: bool = Field(False, validation_alias="DEBUG")

    key_length: int = Field(5, validation_alias="KEY_LENGTH")
