__all__ = ("server",)

import asyncio
import os
import signal
from collections.abc import Sequence
from typing import TYPE_CHECKING

import grpc
import structlog
from dishka import make_async_container
from dishka.integrations.grpcio import DishkaAioInterceptor, GrpcioProvider
from grpc_reflection.v1alpha import reflection

if TYPE_CHECKING:
    from dishka import AsyncContainer, Provider

    from shortener_app.presentation.grpc.interceptors import (
        GrpcInterceptorDefinition,
    )
    from shortener_app.presentation.grpc.services import GrpcServiceDefinition

logger = structlog.get_logger(__name__)


async def server(
    *,
    is_reflection_enable: bool = False,
    ioc_providers: tuple["Provider", ...],
    grpc_interceptors: Sequence["GrpcInterceptorDefinition"],
    grpc_services: Sequence["GrpcServiceDefinition"],
) -> None:
    address = _get_address()

    server_ = await _create_grpc_server(
        is_reflection_enable=is_reflection_enable,
        ioc_providers=ioc_providers,
        grpc_interceptors=grpc_interceptors,
        grpc_services=grpc_services,
    )
    server_.add_insecure_port(address)

    await server_.start()
    logger.info("[gRPC] server started on %s", address)

    stop_event = asyncio.Event()

    def _graceful_shutdown(*_):
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _graceful_shutdown)
        except NotImplementedError:
            # Windows
            pass

    await stop_event.wait()
    logger.info("[gRPC] shutting down...")
    await server_.stop(grace=5)


def _get_address() -> str:
    host = os.getenv("GRPC_HOST", "0.0.0.0")
    port = int(os.getenv("GRPC_PORT", "50051"))
    return f"{host}:{port}"


async def _create_grpc_server(
    *,
    is_reflection_enable: bool,
    ioc_providers: tuple["Provider", ...],
    grpc_interceptors: Sequence["GrpcInterceptorDefinition"],
    grpc_services: Sequence["GrpcServiceDefinition"],
) -> grpc.aio.Server:
    container = make_async_container(
        *ioc_providers,
        GrpcioProvider(),
    )

    return _setup_server(
        is_reflection_enable=is_reflection_enable,
        grpc_interceptors=grpc_interceptors,
        grpc_services=grpc_services,
        ioc_container=container,
    )


def _setup_server(
    *,
    is_reflection_enable: bool,
    ioc_container: "AsyncContainer",
    grpc_interceptors: Sequence["GrpcInterceptorDefinition"],
    grpc_services: Sequence["GrpcServiceDefinition"],
) -> grpc.aio.Server:
    server_ = grpc.aio.server(
        interceptors=[
            *[
                definition.interceptor_cls()
                for definition in grpc_interceptors
            ],
            DishkaAioInterceptor(ioc_container),
        ],
        options=[
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),
        ],
    )

    [
        definition.register(definition.servicer_cls(), server_)
        for definition in grpc_services
    ]

    if is_reflection_enable:
        service_names = (
            *[definition.service_name for definition in grpc_services],
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(service_names, server_)

    return server_
