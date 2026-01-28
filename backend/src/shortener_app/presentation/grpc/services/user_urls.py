__all__ = ("UserUrlsGrpcService",)

from dataclasses import dataclass
from uuid import UUID

import grpc
from dishka.integrations.grpcio import FromDishka, inject

from shortener_app.application.dtos.users import (
    GetUserUrlsDTO,
    PaginationDTO,
    # XUserHeaderDTO,
)
from shortener_app.application.use_cases import GetUserUrlsUseCase
from shortener_app.generated.user_urls.v1 import (
    user_urls_pb2,
    user_urls_pb2_grpc,
)
from shortener_app.presentation.mappers.user_mapper import (
    UserPresentationMapper,
)


@dataclass
class UserUrlsGrpcService(user_urls_pb2_grpc.UserUrlsServiceServicer):
    @inject
    async def GetUserUrls(
        self,
        request: user_urls_pb2.GetUserUrlsRequest,
        context: grpc.aio.ServicerContext,
        use_case: FromDishka[GetUserUrlsUseCase],
        mapper: FromDishka[UserPresentationMapper],
        # header: FromDishka[XUserHeaderDTO],
    ) -> user_urls_pb2.GetUserUrlsResponse:
        # UUID("3b0e3fe7-e753-4e14-9ff4-0a200c2cbdcf")

        result = await use_case.execute(
            user_dto=GetUserUrlsDTO(
                # user_id=UUID(header.x_user_id),
                user_id=UUID("3b0e3fe7-e753-4e14-9ff4-0a200c2cbdcf"),
                pagination_data=PaginationDTO(
                    limit=request.limit,
                    last_id=request.last_id,
                ),
            ),
        )

        return mapper.to_proto_get_user_urls_response(result)
