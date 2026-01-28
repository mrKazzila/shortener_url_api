__all__ = (
    "GRPC_INTERCEPTORS",
    "GrpcInterceptorDefinition",
)

from collections.abc import Sequence
from dataclasses import dataclass

from shortener_app.presentation.grpc.interceptors.reflection_v1_compat import (
    ReflectionV1CompatInterceptor,
)


@dataclass(frozen=True, slots=True)
class GrpcInterceptorDefinition:
    interceptor_cls: type[object]


GRPC_INTERCEPTORS: Sequence[GrpcInterceptorDefinition] = (
    GrpcInterceptorDefinition(interceptor_cls=ReflectionV1CompatInterceptor),
)
