from typing import final

from pydantic import Field

from shortener_app.config.settings._base_settings import BaseAppSettings


@final
class BrokerSettings(BaseAppSettings):
    broker_url: str = Field(
        ...,
        validation_alias="BROKER_URL",
    )
