from src.config import (
    create_app,
    app_setup,
    get_providers,
    get_settings,
)

from src.presentation.api.middleware import MIDDLEWARES
from src.presentation.api.rest import ROUTERS

settings = get_settings()

app = create_app(settings=settings)

app_setup(
    app=app,
    providers=get_providers(),
    middlewares=MIDDLEWARES,
    endpoints=ROUTERS,
)
