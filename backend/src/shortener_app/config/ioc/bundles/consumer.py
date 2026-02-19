__all__ = ("CONSUMER_ONLY_PROVIDERS",)

import structlog
from dishka import Provider, Scope, provide

from shortener_app.application.interfaces import (
    UnitOfWorkProtocol,
)
from shortener_app.application.use_cases.internal import (
    ProcessNewUrlUseCase,
    UpdateUrlUseCase,
)

logger = structlog.get_logger(__name__)


class UseCaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def process_new_url_use_case(
        self,
        uow: UnitOfWorkProtocol,
    ) -> ProcessNewUrlUseCase:
        return ProcessNewUrlUseCase(uow=uow)

    @provide(scope=Scope.REQUEST)
    def update_url_use_case(
        self,
        uow: UnitOfWorkProtocol,
    ) -> UpdateUrlUseCase:
        return UpdateUrlUseCase(uow=uow)


CONSUMER_ONLY_PROVIDERS: tuple[Provider, ...] = (UseCaseProvider(),)
