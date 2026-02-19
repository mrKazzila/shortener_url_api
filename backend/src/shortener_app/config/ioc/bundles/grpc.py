__all__ = ("GRPC_ONLY_PROVIDERS",)

from collections.abc import AsyncIterator
from uuid import UUID

import structlog
from dishka import Provider, Scope, provide
from grpc import ServicerContext

from shortener_app.application.interfaces import (
    CacheProtocol,
    MessageBrokerPublisherProtocol,
    UnitOfWorkProtocol,
)
from shortener_app.application.mappers import UrlDtoFacade
from shortener_app.application.use_cases import (
    CreateUrlUseCase,
    DeleteUrlUseCase,
    GetUserUrlsUseCase,
    RedirectToOriginalUrlUseCase,
    UpdateUrlUseCase,
)
from shortener_app.application.use_cases.internal import (
    CreateUniqKeyUseCase,
    GetTargetByKeyUseCase,
    PublishUrlToBrokerForUpdateUseCase,
    PublishUrlToBrokerUseCase,
)
from shortener_app.domain.services import RandomKeyGenerator
from shortener_app.infrastructures.broker import (
    NewUrlPublishQueue,
)
from shortener_app.infrastructures.codecs import UrlCacheRedisHashCodec
from shortener_app.presentation.exceptions.auth import (
    InvalidUserIdMetadata,
    MissingUserIdMetadata,
)

logger = structlog.get_logger(__name__)


class RandomKeyGeneratorProvider(Provider):
    @provide(scope=Scope.APP)
    def get_random_key_generator(self) -> RandomKeyGenerator:
        return RandomKeyGenerator()


class NewUrlPublishQueueProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_new_url_publish_queue(
        self,
        publish_uc: PublishUrlToBrokerUseCase,
    ) -> AsyncIterator[NewUrlPublishQueue]:
        queue = NewUrlPublishQueue(
            publish_uc=publish_uc,
            maxsize=10_000,
            workers=2,
        )
        await queue.start()
        try:
            yield queue
        finally:
            await queue.stop(drain=True, timeout_sec=10.0)


class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def user_id(self, context: ServicerContext) -> UUID:
        md = dict(context.invocation_metadata())
        raw = md.get("x-user-id")

        # TODO: Just for tests
        if not raw:
            raw = "3b0e3fe7-e753-4e14-9ff4-0a200c2cbdcf"

        if not raw:
            raise MissingUserIdMetadata("missing x-user-id metadata")

        try:
            return UUID(raw)
        except ValueError as e:
            raise InvalidUserIdMetadata("invalid x-user-id metadata") from e


class UseCaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_publish_url_to_broker_use_case(
        self,
        message_broker: MessageBrokerPublisherProtocol,
    ) -> PublishUrlToBrokerUseCase:
        return PublishUrlToBrokerUseCase(
            message_broker=message_broker,
        )

    @provide(scope=Scope.REQUEST)
    def get_create_uniq_key_use_case(
        self,
        key_generator: RandomKeyGenerator,
        cache: CacheProtocol,
        codec: UrlCacheRedisHashCodec,
    ) -> CreateUniqKeyUseCase:
        return CreateUniqKeyUseCase(
            key_generator=key_generator,
            cache=cache,
            codec=codec,
        )

    @provide(scope=Scope.REQUEST)
    def get_create_url_use_case(
        self,
        create_uniq_key_uc: CreateUniqKeyUseCase,
        queue: NewUrlPublishQueue,
        mapper: UrlDtoFacade,
    ) -> CreateUrlUseCase:
        return CreateUrlUseCase(
            create_uniq_key_uc=create_uniq_key_uc,
            publish_url_queue=queue,
            mapper=mapper,
        )

    @provide(scope=Scope.REQUEST)
    def get_target_url_by_key_use_case(
        self,
        cache: CacheProtocol,
        uow: UnitOfWorkProtocol,
        mapper: UrlDtoFacade,
        codec: UrlCacheRedisHashCodec,
    ) -> GetTargetByKeyUseCase:
        return GetTargetByKeyUseCase(
            cache=cache,
            uow=uow,
            mapper=mapper,
            codec=codec,
        )

    @provide(scope=Scope.REQUEST)
    def get_publish_url_to_broker_for_update_use_case(
        self,
        message_broker: MessageBrokerPublisherProtocol,
    ) -> PublishUrlToBrokerForUpdateUseCase:
        return PublishUrlToBrokerForUpdateUseCase(
            message_broker=message_broker,
        )

    @provide(scope=Scope.REQUEST)
    def redirect_to_target_url_use_case(
        self,
        get_target_url_by_key_uc: GetTargetByKeyUseCase,
        get_publish_url_to_broker_uc: PublishUrlToBrokerForUpdateUseCase,
        mapper: UrlDtoFacade,
    ) -> RedirectToOriginalUrlUseCase:
        return RedirectToOriginalUrlUseCase(
            get_target_url_by_key_uc=get_target_url_by_key_uc,
            publish_url_to_broker_for_update_uc=get_publish_url_to_broker_uc,
            mapper=mapper,
        )

    @provide(scope=Scope.REQUEST)
    def get_user_urls_use_case(
        self,
        uow: UnitOfWorkProtocol,
        mapper: UrlDtoFacade,
    ) -> GetUserUrlsUseCase:
        return GetUserUrlsUseCase(
            uow=uow,
            mapper=mapper,
        )

    @provide(scope=Scope.REQUEST)
    def delete_url_use_case(
        self,
        get_target_url_by_key_uc: GetTargetByKeyUseCase,
        cache: CacheProtocol,
        uow: UnitOfWorkProtocol,
    ) -> DeleteUrlUseCase:
        return DeleteUrlUseCase(
            get_target_url_by_key_uc=get_target_url_by_key_uc,
            cache=cache,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def update_url_use_case(
        self,
        get_target_url_by_key_uc: GetTargetByKeyUseCase,
        uow: UnitOfWorkProtocol,
    ) -> UpdateUrlUseCase:
        return UpdateUrlUseCase(
            get_target_url_by_key_uc=get_target_url_by_key_uc,
            uow=uow,
        )


GRPC_ONLY_PROVIDERS: tuple[Provider, ...] = (
    RandomKeyGeneratorProvider(),
    AuthProvider(),
    UseCaseProvider(),
    NewUrlPublishQueueProvider(),
)
