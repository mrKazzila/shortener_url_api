__all__ = ("UserUrlsGrpcService",)

from dataclasses import dataclass
from uuid import UUID

import grpc
from dishka.integrations.grpcio import FromDishka, inject
from shortener_app.generated.user_urls.v1 import (
    user_urls_pb2,
    user_urls_pb2_grpc,
)

from shortener_app.application.dtos.users.user_requests import (
    GetUserUrlsDTO,
    PaginationDTO,
)
from shortener_app.application.use_cases import GetUserUrlsUseCase
from shortener_app.presentation.mappers import (
    UserPresentationMapper,
)


@dataclass
class UserUrlsGrpcService(user_urls_pb2_grpc.UserUrlsServiceServicer):
    @inject
    async def GetUserUrls(
        self,
        request: user_urls_pb2.GetUserUrlsRequest,
        context: grpc.aio.ServicerContext,
        x_user_id: FromDishka[UUID],
        use_case: FromDishka[GetUserUrlsUseCase],
        mapper: FromDishka[UserPresentationMapper],
    ) -> user_urls_pb2.GetUserUrlsResponse:
        result = await use_case.execute(
            user_dto=GetUserUrlsDTO(
                user_id=x_user_id,
                pagination_data=PaginationDTO(
                    limit=request.limit,
                    last_id=request.last_id,
                ),
            ),
        )

        return mapper.to_proto_get_user_urls_response(result)
