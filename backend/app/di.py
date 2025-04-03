from dishka import Provider, Scope, provide
from app.service_layer.unit_of_work import UnitOfWork
from app.service_layer.services.urls import UrlsServices


__all__ = ("ServiceProvider",)


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_uow(self) -> UnitOfWork:
        return UnitOfWork()

    @provide(scope=Scope.REQUEST)
    def provide_url_service(self) -> UrlsServices:
        return UrlsServices()
