__all__ = (
    "get_settings",
    "server",
)

from shortener_app.config.settings.loader import get_settings
from shortener_app.config.setup import server
