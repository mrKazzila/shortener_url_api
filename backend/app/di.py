from dishka import (
    AsyncContainer,
    Provider,
    Scope,
    make_async_container,
    provide,
)
from dishka.integrations.fastapi import FastapiProvider
from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.urls import XUserHeader
from app.exceptions.auth import UserHeaderNotFoundException
from app.service_layer.cqrs import QueryService, UrlCommandService
from app.service_layer.services import InfoServices, UrlsServices
from app.service_layer.unit_of_work import UnitOfWork
from app.settings.config import settings
from app.settings.database import async_session_maker
from app.settings.redis_config import get_redis

__all__ = ("container_setup",)


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_user_id(self, request: Request) -> XUserHeader:
        if not (user_id := request.headers.get(settings.USER_HEADER)):
            raise UserHeaderNotFoundException()
        return XUserHeader(user_id)

    @provide(scope=Scope.REQUEST)
    async def provide_async_session(self) -> AsyncSession:
        return async_session_maker()

    @provide(scope=Scope.REQUEST)
    def provide_uow(self) -> UnitOfWork:
        return UnitOfWork(session_factory=async_session_maker)

    @provide(scope=Scope.APP)
    def provide_query_service(self) -> QueryService:
        return QueryService(session_factory=async_session_maker)

    @provide(scope=Scope.REQUEST)
    def provide_url_command_service(
        self,
        uow: UnitOfWork,
    ) -> UrlCommandService:
        return UrlCommandService(uow=uow)

    @provide(scope=Scope.APP)
    async def provide_redis(self) -> Redis:
        return await get_redis()

    @provide(scope=Scope.REQUEST)
    def provide_url_service(
        self,
        redis: Redis,
        query_service: QueryService,
        command_service: UrlCommandService,
    ) -> UrlsServices:
        return UrlsServices(
            redis=redis,
            query_service=query_service,
            command_service=command_service,
        )

    @provide(scope=Scope.APP)
    def provide_info_service(self) -> InfoServices:
        return InfoServices()


def container_setup() -> AsyncContainer:
    return make_async_container(ServiceProvider(), FastapiProvider())
