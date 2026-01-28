__all__ = ("ShortenerGrpcService",)

from dataclasses import dataclass
from uuid import UUID

import grpc
from dishka.integrations.grpcio import FromDishka, inject

from shortener_app.application.dtos.urls import (
    CreateUrlDTO,
    DeleteUrlDTO,
    UpdateUrlDTO,
)
from shortener_app.application.use_cases import (
    CreateUrlUseCase,
    DeleteUrlUseCase,
    RedirectToOriginalUrlUseCase,
    UpdateUrlUseCase,
)
from shortener_app.generated.shortener.v1 import (
    shortener_pb2,
    shortener_pb2_grpc,
)


@dataclass
class ShortenerGrpcService(shortener_pb2_grpc.ShortenerServiceServicer):
    @inject
    async def CreateShortUrl(
        self,
        request: shortener_pb2.CreateShortUrlRequest,
        context: grpc.aio.ServicerContext,
        use_case: FromDishka[CreateUrlUseCase],
        # header: FromDishka[XUserHeaderDTO],
    ) -> shortener_pb2.CreateShortUrlResponse:
        result = await use_case.execute(
            dto=CreateUrlDTO(
                target_url=request.target_url,
                # user_id=UUID(header.x_user_id),
                user_id=UUID("3b0e3fe7-e753-4e14-9ff4-0a200c2cbdcf"),
            ),
        )

        return shortener_pb2.CreateShortUrlResponse(
            key=result.key,
            target_url=result.target_url,
        )

    @inject
    async def ResolveKey(
        self,
        request: shortener_pb2.ResolveKeyRequest,
        context: grpc.aio.ServicerContext,
        use_case: FromDishka[RedirectToOriginalUrlUseCase],
    ) -> shortener_pb2.ResolveKeyResponse:
        result = await use_case.execute(key=request.key)
        return shortener_pb2.ResolveKeyResponse(target_url=result)

    @inject
    async def UpdateUrl(
        self,
        request: shortener_pb2.UpdateUrlRequest,
        context: grpc.aio.ServicerContext,
        use_case: FromDishka[UpdateUrlUseCase],
        # header: FromDishka[XUserHeaderDTO],
    ) -> str:
        result = await use_case.execute(
            dto=UpdateUrlDTO(
                key=request.key,
                is_active=request.is_active,
                name=request.name,
            ),
        )

        return "Ok" if result else "Error"

    @inject
    async def DeleteUrl(
        self,
        request: shortener_pb2.DeleteUrlRequest,
        context: grpc.aio.ServicerContext,
        use_case: FromDishka[DeleteUrlUseCase],
        # header: FromDishka[XUserHeaderDTO],
    ) -> str:
        result = await use_case.execute(
            dto=DeleteUrlDTO(key=request.key),
        )

        return "Ok" if result else "Error"
