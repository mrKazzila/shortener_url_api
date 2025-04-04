from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.domain.urls_repository import UrlsRepository
from app.service_layer.services.urls import UrlsServices
from app.service_layer.unit_of_work import UnitOfWork
from app.settings.database import async_session_maker

__all__ = ("ServiceProvider",)


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_async_session(self) -> AsyncSession:
        return async_session_maker()

    @provide(scope=Scope.REQUEST)
    def provide_urls_repo(self, session: AsyncSession) -> UrlsRepository:
        return UrlsRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def provide_uow(self, session: AsyncSession) -> UnitOfWork:
        uow = UnitOfWork()
        uow._session = session
        return uow

    @provide(scope=Scope.REQUEST)
    def provide_url_service(self, uow: UnitOfWork) -> UrlsServices:
        return UrlsServices(uow=uow)
