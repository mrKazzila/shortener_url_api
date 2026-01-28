__all__ = (
    "GRPC_SERVICES",
    "GrpcServiceDefinition",
)

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import grpc

from shortener_app.generated.shortener.v1 import shortener_pb2_grpc
from shortener_app.generated.user_urls.v1 import user_urls_pb2_grpc
from shortener_app.presentation.grpc.services.shortener import (
    ShortenerGrpcService,
)
from shortener_app.presentation.grpc.services.user_urls import (
    UserUrlsGrpcService,
)


@dataclass(frozen=True, slots=True)
class GrpcServiceDefinition:
    register: Callable[[object, grpc.aio.Server], None]
    servicer_cls: type[object]
    service_name: str


GRPC_SERVICES: Sequence[GrpcServiceDefinition] = (
    GrpcServiceDefinition(
        register=shortener_pb2_grpc.add_ShortenerServiceServicer_to_server,
        servicer_cls=ShortenerGrpcService,
        service_name="shortener.v1.ShortenerService",
    ),
    GrpcServiceDefinition(
        register=user_urls_pb2_grpc.add_UserUrlsServiceServicer_to_server,
        servicer_cls=UserUrlsGrpcService,
        service_name="user_urls.v1.UserUrlsService",
    ),
)
