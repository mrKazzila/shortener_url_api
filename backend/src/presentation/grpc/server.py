__all__ = ("create_grpc_server",)

import grpc
from dishka import make_async_container, AsyncContainer
from dishka.integrations.grpcio import DishkaAioInterceptor, GrpcioProvider
from grpc_reflection.v1alpha import reflection

from src.config.ioc.providers import PROVIDERS
from src.generated.shortener.v1 import shortener_pb2_grpc
from src.generated.user_urls.v1 import user_urls_pb2_grpc
from src.presentation.grpc.interceptors import ReflectionV1CompatInterceptor
from src.presentation.grpc.services import (
    ShortenerGrpcService,
    UserUrlsGrpcService,
)


async def create_grpc_server() -> grpc.aio.Server:
    container = make_async_container(
        *PROVIDERS,
        GrpcioProvider(),
    )

    return _setup_server(ioc_container=container)


def _setup_server(ioc_container: AsyncContainer) -> grpc.aio.Server:
    server = grpc.aio.server(
        interceptors=[
            ReflectionV1CompatInterceptor(),
            DishkaAioInterceptor(ioc_container),
        ],
        options=[
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),
        ],
    )

    user_urls_pb2_grpc.add_UserUrlsServiceServicer_to_server(
        UserUrlsGrpcService(),
        server,
    )

    shortener_pb2_grpc.add_ShortenerServiceServicer_to_server(
        ShortenerGrpcService(),
        server,
    )

    service_names = (
        "user_urls.v1.UserUrlsService",
        "shortener.v1.ShortenerService",
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)

    return server
