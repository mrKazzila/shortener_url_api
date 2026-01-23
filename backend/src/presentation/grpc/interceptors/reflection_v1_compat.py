__all__ = ("ReflectionV1CompatInterceptor",)

import grpc
from grpc_reflection.v1alpha import reflection_pb2


class ReflectionV1CompatInterceptor(grpc.aio.ServerInterceptor):
    _V1_METHOD = "/grpc.reflection.v1.ServerReflection/ServerReflectionInfo"

    async def intercept_service(self, continuation, handler_call_details):
        if handler_call_details.method == self._V1_METHOD:

            async def _unimplemented(request_iterator, context):
                await context.abort(
                    grpc.StatusCode.UNIMPLEMENTED,
                    "Reflection v1 is not supported, use v1alpha.",
                )
                if False:
                    yield  # pragma: no cover

            return grpc.stream_stream_rpc_method_handler(
                _unimplemented,
                request_deserializer=reflection_pb2.ServerReflectionRequest.FromString,
                response_serializer=reflection_pb2.ServerReflectionResponse.SerializeToString,
            )

        return await continuation(handler_call_details)
