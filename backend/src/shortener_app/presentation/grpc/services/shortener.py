__all__ = ("ShortenerGrpcService",)

from dataclasses import dataclass
from uuid import UUID

import grpc
from dishka.integrations.grpcio import FromDishka, inject
from shortener_app.generated.shortener.v1 import (
    shortener_pb2,
    shortener_pb2_grpc,
)

from shortener_app.application.use_cases import (
    CreateUrlUseCase,
    DeleteUrlUseCase,
    RedirectToOriginalUrlUseCase,
    UpdateUrlUseCase,
)
from shortener_app.presentation.mappers import UrlPresentationMapper


@dataclass
class ShortenerGrpcService(shortener_pb2_grpc.ShortenerServiceServicer):
    @inject
    async def CreateShortUrl(
        self,
        request: shortener_pb2.CreateShortUrlRequest,
        context: grpc.aio.ServicerContext,
        x_user_id: FromDishka[UUID],
        mapper: FromDishka[UrlPresentationMapper],
        use_case: FromDishka[CreateUrlUseCase],
    ) -> shortener_pb2.CreateShortUrlResponse:
        result = await use_case.execute(
            dto=mapper.to_create_url_dto(
                request,
                user_id=x_user_id,
            ),
        )
        return mapper.to_create_short_url_response(result)

    @inject
    async def ResolveKey(
        self,
        request: shortener_pb2.ResolveKeyRequest,
        context: grpc.aio.ServicerContext,
        use_case: FromDishka[RedirectToOriginalUrlUseCase],
        mapper: FromDishka[UrlPresentationMapper],
    ) -> shortener_pb2.ResolveKeyResponse:
        return mapper.to_resolve_key_response(
            await use_case.execute(key=request.key),
        )

    @inject
    async def UpdateUrl(
        self,
        request: shortener_pb2.UpdateUrlRequest,
        context: grpc.aio.ServicerContext,
        x_user_id: FromDishka[UUID],
        use_case: FromDishka[UpdateUrlUseCase],
        mapper: FromDishka[UrlPresentationMapper],
    ) -> shortener_pb2.UpdateUrlResponse:
        return mapper.to_update_url_response(
            ok=await use_case.execute(
                dto=mapper.to_update_url_dto(request),
            ),
        )

    @inject
    async def DeleteUrl(
        self,
        request: shortener_pb2.DeleteUrlRequest,
        context: grpc.aio.ServicerContext,
        x_user_id: FromDishka[UUID],
        use_case: FromDishka[DeleteUrlUseCase],
        mapper: FromDishka[UrlPresentationMapper],
    ) -> shortener_pb2.DeleteUrlResponse:
        return mapper.to_delete_url_response(
            ok=await use_case.execute(
                dto=mapper.to_delete_url_dto(request),
            ),
        )
