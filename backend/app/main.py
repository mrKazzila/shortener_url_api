from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka

from app.api import MIDDLEWARES, ROUTERS
from app.di import ServiceProvider
from app.settings import create_app, middlewares_setup, routers_setup

container = make_async_container(ServiceProvider())

app = create_app(
    title="ShortenerApi",
    description="Simple API for url shortener logic",
    version="0.0.1",
    contact={
        "autor": "mrkazzila@gmail.com",
    },
)


setup_dishka(container=container, app=app)
routers_setup(app=app, endpoints=ROUTERS)
middlewares_setup(app=app, middlewares=MIDDLEWARES)
