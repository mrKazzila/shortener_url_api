from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.service_layer.services.urls import UrlsServices
from app.service_layer.unit_of_work import UnitOfWork
from app.settings.database import async_session_maker

__all__ = ("ServiceProvider",)


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_async_session(self) -> AsyncSession:
        return async_session_maker()

    @provide(scope=Scope.APP)
    def provide_uow(self) -> UnitOfWork:
        return UnitOfWork(session_factory=async_session_maker)

    @provide(scope=Scope.APP)
    def provide_url_service(self, uow: UnitOfWork) -> UrlsServices:
        return UrlsServices(uow=uow)
