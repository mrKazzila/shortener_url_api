__all__ = (
    "get_providers",
    "get_settings",
    "server",
)

from shortener_app.config.ioc.di import get_providers
from shortener_app.config.settings.loader import get_settings
from shortener_app.config.setup import server
