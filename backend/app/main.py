from app.api import MIDDLEWARES, ROUTERS
from app.di import container_setup
from app.settings import create_app, di_setup, middlewares_setup, routers_setup

app = create_app(
    title="ShortenerApi",
    description="Simple API for url shortener logic",
    version="0.0.1",
    contact={
        "autor": "mrkazzila@gmail.com",
    },
)

di_setup(app=app, containers=container_setup())
routers_setup(app=app, endpoints=ROUTERS)
middlewares_setup(app=app, middlewares=MIDDLEWARES)
