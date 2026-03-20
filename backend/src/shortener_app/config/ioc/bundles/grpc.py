__all__ = ("GRPC_ONLY_PROVIDERS",)

from collections.abc import AsyncIterator
from random import SystemRandom
from uuid import UUID

import structlog
from dishka import Provider, Scope, provide
from grpc import ServicerContext

from shortener_app.application.interfaces.broker import (
    MessageBrokerPublisherProtocol,
)
from shortener_app.application.interfaces.cache import CacheProtocol
from shortener_app.application.interfaces.publish_queue import (
    NewUrlPublishQueueProtocol,
)
from shortener_app.application.interfaces.uow import UnitOfWorkProtocol
from shortener_app.application.mappers.url_dto_facade import UrlDtoFacade
from shortener_app.application.services.urls.key_reservation import (
    UrlKeyReservationService,
)
from shortener_app.application.services.urls.url_cache import UrlCacheService
from shortener_app.application.services.urls.url_enqueue import (
    UrlPublishEnqueueService,
)
from shortener_app.application.services.urls.url_publisher import (
    UrlBrokerPublishService,
)
from shortener_app.application.services.urls.url_reader import UrlReaderService
from shortener_app.application.use_cases.create_short_url import (
    CreateUrlUseCase,
)
from shortener_app.application.use_cases.delete_url import DeleteUrlUseCase
from shortener_app.application.use_cases.get_user_urls import (
    GetUserUrlsUseCase,
)
from shortener_app.application.use_cases.redirect_to_original_url import (
    RedirectToOriginalUrlUseCase,
)
from shortener_app.application.use_cases.update_url import UpdateUrlUseCase
from shortener_app.config.ioc.adapters.new_url_publish_queue import (
    NewUrlPublishQueueAdapter,
)
from shortener_app.config.settings import Settings
from shortener_app.domain.services.key_generator import RandomKeyGenerator
from shortener_app.infrastructures.broker import NewUrlPublishQueue
from shortener_app.infrastructures.codecs.cache.url_redis_hash_codec import (
    UrlCacheRedisHashCodec,
)
from shortener_app.presentation.exceptions.auth import (
    InvalidUserIdMetadata,
    MissingUserIdMetadata,
)
from shortener_app.presentation.mappers import (
    UrlPresentationMapper,
    UserPresentationMapper,
)

logger = structlog.get_logger(__name__)


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


class RandomKeyGeneratorProvider(Provider):
    @provide(scope=Scope.APP)
    def get_random_key_generator(
        self,
        settings: Settings,
    ) -> RandomKeyGenerator:
        return RandomKeyGenerator(
            length=settings.app.key_length,
            random=SystemRandom(),
        )


class NewUrlPublishQueueProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_new_url_publish_queue(
        self,
        broker_publish_service: UrlBrokerPublishService,
    ) -> AsyncIterator[NewUrlPublishQueueProtocol]:
        impl = NewUrlPublishQueue(
            broker_publish_service=broker_publish_service,
            maxsize=10_000,
            workers=2,
        )
        await impl.start()
        try:
            yield NewUrlPublishQueueAdapter(impl)
        finally:
            await impl.stop(drain=True, timeout_sec=10.0)


class PresentationMapperProvider(Provider):
    @provide(scope=Scope.APP)
    def get_url_presentation_mapper(self) -> UrlPresentationMapper:
        return UrlPresentationMapper()

    @provide(scope=Scope.APP)
    def get_user_presentation_mapper(self) -> UserPresentationMapper:
        return UserPresentationMapper()


class ServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def get_cache_service(
        self,
        cache: CacheProtocol,
        mapper: UrlDtoFacade,
        codec: UrlCacheRedisHashCodec,
    ) -> UrlCacheService:
        return UrlCacheService(
            cache=cache,
            mapper=mapper,
            codec=codec,
        )

    @provide(scope=Scope.APP)
    def get_key_reservation_service(
        self,
        key_generator: RandomKeyGenerator,
        cache_service: UrlCacheService,
    ) -> UrlKeyReservationService:
        return UrlKeyReservationService(
            key_generator=key_generator,
            cache_service=cache_service,
        )

    @provide(scope=Scope.APP)
    def get_publish_enqueue_service(
        self,
        new_urls_queue: NewUrlPublishQueueProtocol,
    ) -> UrlPublishEnqueueService:
        return UrlPublishEnqueueService(new_urls_queue=new_urls_queue)

    @provide(scope=Scope.APP)
    def get_url_broker_publish_service(
        self,
        message_broker: MessageBrokerPublisherProtocol,
    ) -> UrlBrokerPublishService:
        return UrlBrokerPublishService(message_broker=message_broker)

    @provide(scope=Scope.APP)
    def get_url_reader_service(
        self,
        cache_service: UrlCacheService,
    ) -> UrlReaderService:
        return UrlReaderService(cache_service=cache_service)


class UseCaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_create_url_use_case(
        self,
        key_reservation_service: UrlKeyReservationService,
        publish_enqueue_service: UrlPublishEnqueueService,
        mapper: UrlDtoFacade,
    ) -> CreateUrlUseCase:
        return CreateUrlUseCase(
            key_reservation_service=key_reservation_service,
            publish_enqueue_service=publish_enqueue_service,
            mapper=mapper,
        )

    @provide(scope=Scope.REQUEST)
    def redirect_to_target_url_use_case(
        self,
        reader_service: UrlReaderService,
        broker_publish_service: UrlBrokerPublishService,
        mapper: UrlDtoFacade,
        uow: UnitOfWorkProtocol,
    ) -> RedirectToOriginalUrlUseCase:
        return RedirectToOriginalUrlUseCase(
            reader_service=reader_service,
            broker_publish_service=broker_publish_service,
            mapper=mapper,
            uow=uow,
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
        reader_service: UrlReaderService,
        cache: CacheProtocol,
        uow: UnitOfWorkProtocol,
    ) -> DeleteUrlUseCase:
        return DeleteUrlUseCase(
            reader_service=reader_service,
            cache=cache,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def update_url_use_case(
        self,
        reader_service: UrlReaderService,
        uow: UnitOfWorkProtocol,
    ) -> UpdateUrlUseCase:
        return UpdateUrlUseCase(
            reader_service=reader_service,
            uow=uow,
        )


GRPC_ONLY_PROVIDERS: tuple[Provider, ...] = (
    AuthProvider(),
    RandomKeyGeneratorProvider(),
    NewUrlPublishQueueProvider(),
    PresentationMapperProvider(),
    ServiceProvider(),
    UseCaseProvider(),
)
