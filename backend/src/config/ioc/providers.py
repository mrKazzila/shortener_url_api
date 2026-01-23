__all__ = ("PROVIDERS",)

from collections.abc import AsyncIterator

import redis.asyncio as redis
import structlog
from dishka import Provider, Scope, provide
from faststream.kafka import KafkaBroker
from grpc import ServicerContext
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from src.application.dtos.users import XUserHeaderDTO
from src.application.interfaces import (
    CacheProtocol,
    MessageBrokerPublisherProtocol,
    RepositoryProtocol,
    UnitOfWorkProtocol,
)
from src.application.mappers import UrlMapper
from src.application.use_cases import (
    CreateUrlUseCase,
    GetUserUrlsUseCase,
    RedirectToOriginalUrlUseCase,
    DeleteUrlUseCase,
    UpdateUrlUseCase,
)
from src.application.use_cases.internal import (
    CreateUniqKeyUseCase,
    GetTargetByKeyUseCase,
    PublishUrlToBrokerForUpdateUseCase,
    PublishUrlToBrokerUseCase,
)
from src.config.settings import Settings
from src.domain.services.key_generator import RandomKeyGenerator
from src.infrastructures.broker import KafkaPublisher, NewUrlPublishQueue
from src.infrastructures.cache import RedisCacheClient
from src.infrastructures.db import (
    SQLAlchemyRepository,
    UnitOfWork,
    engine_factory,
    get_session_factory,
)
from src.infrastructures.mappers import UrlDBMapper
from src.presentation.mappers import (
    UrlPresentationMapper,
    UserPresentationMapper,
)

logger = structlog.get_logger(__name__)


class SettingsProvider(Provider):

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return Settings()


class AuthProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def user_id(self, context: ServicerContext) -> XUserHeaderDTO:
        md = dict(context.invocation_metadata())
        raw = md.get("x-user-id")

        if not raw:
            raise ValueError("missing x-user-id metadata")

        return XUserHeaderDTO(x_user_id=raw)


class RandomKeyGeneratorProvider(Provider):

    @provide(scope=Scope.APP)
    def get_random_key_generator(self) -> RandomKeyGenerator:
        return RandomKeyGenerator()


class BrokerProvider(Provider):

    @provide(scope=Scope.APP)
    async def get_broker(
        self,
        settings: Settings,
    ) -> AsyncIterator[KafkaBroker]:
        broker = KafkaBroker(
            [settings.broker_url],
            enable_idempotence=True,
            linger_ms=20,
        )

        try:
            await broker.start()
            logger.info(
                "Kafka broker started successfully",
                url=settings.broker_url,
            )
            yield broker
        except Exception as e:
            logger.error("Failed to start Kafka broker", error=str(e))
            raise
        finally:
            await broker.stop()


class DatabaseProvider(Provider):

    @provide(scope=Scope.APP)
    async def get_session_factory(
        self,
        settings: Settings,
    ) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
        engine = engine_factory(
            dsn=str(settings.database_url),
            is_echo=settings.debug,
        )
        session_factory = get_session_factory(engine)

        try:
            yield session_factory
        finally:
            await engine.dispose()

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self,
        factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session


class MapperProvider(Provider):

    @provide(scope=Scope.APP)
    def get_url_mapper(self) -> UrlMapper:
        return UrlMapper()

    @provide(scope=Scope.REQUEST)
    def get_db_mapper(self) -> UrlDBMapper:
        return UrlDBMapper()

    @provide(scope=Scope.REQUEST)
    def get_url_presentation_mapper(self) -> UrlPresentationMapper:
        return UrlPresentationMapper()

    @provide(scope=Scope.REQUEST)
    def get_user_presentation_mapper(self) -> UserPresentationMapper:
        return UserPresentationMapper()


class RepositoryProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def get_repository(
        self,
        session: AsyncSession,
        db_mapper: UrlDBMapper,
    ) -> RepositoryProtocol:
        return SQLAlchemyRepository(
            session=session,
            mapper=db_mapper,
        )


class UnitOfWorkProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def get_unit_of_work(
        self,
        session: AsyncSession,
        repository: RepositoryProtocol,
    ) -> UnitOfWorkProtocol:
        return UnitOfWork(
            session=session,
            repository=repository,
        )


class ServiceProvider(Provider):

    @provide(scope=Scope.APP)
    def get_message_broker(
        self,
        broker: KafkaBroker,
        url_mapper: UrlMapper,
    ) -> MessageBrokerPublisherProtocol:
        return KafkaPublisher(
            broker=broker,
            mapper=url_mapper,
        )


class CacheProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_cache_service(
        self,
        settings: Settings,
    ) -> AsyncIterator[CacheProtocol]:
        redis_client = redis.from_url(
            str(settings.redis_url),
            encoding="utf-8",
            decode_responses=False,
            retry_on_timeout=True,
            health_check_interval=60,
            max_connections=200,
            socket_connect_timeout=1.0,
            socket_timeout=1.0,
        )
        cache_service = RedisCacheClient(
            client=redis_client,
            ttl=settings.redis_cache_ttl,
        )

        try:
            await redis_client.ping()
        except Exception:
            raise

        try:
            yield cache_service
        finally:
            await cache_service.close()


class UseCaseProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def get_create_uniq_key_use_case(
        self,
        key_generator: RandomKeyGenerator,
        cache: CacheProtocol,
    ) -> CreateUniqKeyUseCase:
        return CreateUniqKeyUseCase(
            key_generator=key_generator,
            cache=cache,
        )

    @provide(scope=Scope.APP)
    def get_publish_url_to_broker_use_case(
        self,
        message_broker: MessageBrokerPublisherProtocol,
    ) -> PublishUrlToBrokerUseCase:
        return PublishUrlToBrokerUseCase(
            message_broker=message_broker,
        )

    @provide(scope=Scope.REQUEST)
    def get_create_url_use_case(
        self,
        create_uniq_key_uc: CreateUniqKeyUseCase,
        queue: NewUrlPublishQueue,
    ) -> CreateUrlUseCase:
        return CreateUrlUseCase(
            create_uniq_key_uc=create_uniq_key_uc,
            publish_url_queue=queue,
        )

    @provide(scope=Scope.REQUEST)
    def get_target_url_by_key_use_case(
        self,
        cache: CacheProtocol,
        uow: UnitOfWorkProtocol,
        mapper: UrlMapper,
    ) -> GetTargetByKeyUseCase:
        return GetTargetByKeyUseCase(cache=cache, uow=uow, mapper=mapper)

    @provide(scope=Scope.REQUEST)
    def get_publish_url_to_broker_for_update_use_case(
        self,
        message_broker: MessageBrokerPublisherProtocol,
    ) -> PublishUrlToBrokerForUpdateUseCase:
        return PublishUrlToBrokerForUpdateUseCase(message_broker=message_broker)

    @provide(scope=Scope.REQUEST)
    def redirect_to_target_url_use_case(
        self,
        get_target_url_by_key_uc: GetTargetByKeyUseCase,
        get_publish_url_to_broker_uc: PublishUrlToBrokerForUpdateUseCase,
    ) -> RedirectToOriginalUrlUseCase:
        return RedirectToOriginalUrlUseCase(
            get_target_url_by_key_uc=get_target_url_by_key_uc,
            publish_url_to_broker_for_update_uc=get_publish_url_to_broker_uc,
        )

    @provide(scope=Scope.REQUEST)
    def get_user_urls_use_case(
        self,
        uow: UnitOfWorkProtocol,
    ) -> GetUserUrlsUseCase:
        return GetUserUrlsUseCase(uow=uow)

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


PROVIDERS: list[Provider] = [
    SettingsProvider(),
    RandomKeyGeneratorProvider(),
    AuthProvider(),
    CacheProvider(),
    BrokerProvider(),
    MapperProvider(),
    DatabaseProvider(),
    RepositoryProvider(),
    UnitOfWorkProvider(),
    ServiceProvider(),
    UseCaseProvider(),
    NewUrlPublishQueueProvider(),
]
