from dishka import Provider, Scope, provide
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.urls import XUserHeader
from app.exceptions.auth import UserHeaderNotFoundException
from app.service_layer.services import InfoServices, UrlsServices
from app.service_layer.unit_of_work import UnitOfWork
from app.settings.config import settings
from app.settings.database import async_session_maker

__all__ = ("ServiceProvider",)


class ServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_uow(self) -> UnitOfWork:
        return UnitOfWork(session_factory=async_session_maker)

    @provide(scope=Scope.APP)
    def provide_url_service(self, uow: UnitOfWork) -> UrlsServices:
        return UrlsServices(uow=uow)

    @provide(scope=Scope.APP)
    def provide_info_service(self) -> InfoServices:
        return InfoServices()

    @provide(scope=Scope.REQUEST)
    async def provide_async_session(self) -> AsyncSession:
        return async_session_maker()

    @provide(scope=Scope.REQUEST)
    async def get_user_id(self, request: Request) -> XUserHeader:
        if not (user_id := request.headers.get(settings.USER_HEADER)):
            raise UserHeaderNotFoundException()
        return XUserHeader(user_id)
