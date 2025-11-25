from collections.abc import AsyncIterator

import redis.asyncio as redis
import structlog
from dishka import FromDishka
from dishka import Provider, Scope, provide
from fastapi import Request
from faststream.kafka import KafkaBroker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from src.application.dtos.users import XUserHeaderDTO
from src.application.interfaces.broker import MessageBrokerPublisherProtocol
from src.application.interfaces.cache import CacheProtocol
from src.application.interfaces.uow import UnitOfWorkProtocol
from src.application.use_cases.create_short_url import CreateUrlUseCase
from src.application.use_cases.get_user_urls import GetUserUrlsUseCase
from src.application.use_cases.internal.add_new_url_to_cache import AddNewUrlToCacheUseCase
from src.application.use_cases.internal.check_key_in_cashe import CheckKeyInCacheUseCase
from src.application.use_cases.internal.create_uniq_key_in_cache import CreateUniqKeyInCacheUseCase
from src.application.use_cases.internal.get_target_url_by_key import GetTargetByKeyUseCase
from src.application.use_cases.internal.publish_data_to_broker import PublishUrlToBrokerUseCase
from src.application.use_cases.internal.publish_to_broker_for_update import PublishUrlToBrokerForUpdateUseCase
from src.application.use_cases.redirect_to_original_url import RedirectToOriginalUrlUseCase
from src.config.settings import Settings
from src.domain.services.key_generator import RandomKeyGenerator
from src.infrastructures.broker.publisher import KafkaPublisher
from src.infrastructures.cache.redis_client import RedisCacheClient
from src.infrastructures.db.repository import SQLAlchemyRepository
from src.infrastructures.db.session import engine_factory, get_session_factory
from src.infrastructures.db.uow import UnitOfWork

__all__ = (
    "PROVIDERS",
)

logger = structlog.get_logger(__name__)


class SettingsProvider(Provider):
    """
    Provides application config.
    """

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        """
        Provides the Settings instance.
        """
        return Settings()


class AuthProvider(Provider):
    """Provides current user from headers."""

    # TODO: Refactor

    def __init__(self):
        super().__init__()
        print("AuthProvider initialized!")

    @provide(scope=Scope.REQUEST)
    def get_x_user_header_dto(
        self,
        request: Request,
        settings: FromDishka[Settings],
    ) -> XUserHeaderDTO:
        print(f"Headers: {dict(request.headers)}")
        user_id = request.headers.get(settings.user_header)
        print(f"Extracted user_id: {user_id}")
        return XUserHeaderDTO(x_user_id=user_id)


class RandomKeyGeneratorProvider(Provider):
    """
    Provides RandomKeyGenerator.
    """

    @provide(scope=Scope.APP)
    def get_random_key_generator(self) -> RandomKeyGenerator:
        return RandomKeyGenerator()


class BrokerProvider(Provider):
    """
    Provides a Kafka message broker instance.
    """

    @provide(scope=Scope.APP)
    async def get_broker(
        self,
        settings: Settings,
    ) -> AsyncIterator[KafkaBroker]:
        """
        Provides a KafkaBroker instance.
        """
        broker = KafkaBroker([settings.broker_url])

        try:
            await broker.start()
            logger.info(
                "Kafka broker started successfully",
                url=settings.broker_url,
                queue=settings.broker_new_artifact_queue
            )
            yield broker
        except Exception as e:
            logger.error("Failed to start Kafka broker", error=str(e))
            raise
        finally:
            await broker.stop()


class DatabaseProvider(Provider):
    """
    Provides database-related dependencies, such as session factory and sessions.
    """

    @provide(scope=Scope.APP)
    async def get_session_factory(
        self,
        settings: Settings,
    ) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
        """
        Provides an asynchronous session factory for SQLAlchemy.
        """
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
        """
        Provides an asynchronous SQLAlchemy session.
        """
        async with factory() as session:
            yield session


class RepositoryProvider(Provider):
    """
    Provides repository implementations.
    """

    @provide(scope=Scope.REQUEST)
    def get_artifact_repository(
        self,
        session: AsyncSession,
    ) -> SQLAlchemyRepository:
        """
        Provides an ArtifactRepositoryProtocol implementation.
        """
        return SQLAlchemyRepository(session=session)


class UnitOfWorkProvider(Provider):
    """
    Provides Unit of Work implementations.
    """

    @provide(scope=Scope.REQUEST)
    def get_unit_of_work(
        self,
        session: AsyncSession,
        repository: SQLAlchemyRepository,
    ) -> UnitOfWorkProtocol:
        """
        Provides a UnitOfWorkProtocol implementation.
        """
        return UnitOfWork(
            session=session,
            repository=repository,
        )


class ServiceProvider(Provider):
    """
    Provides service clients for external integrations.
    """

    @provide(scope=Scope.REQUEST)
    def get_message_broker(
        self,
        broker: KafkaBroker,
    ) -> MessageBrokerPublisherProtocol:
        """
        Provides a MessageBrokerPublisherProtocol implementation.
        """
        return KafkaPublisher(broker=broker)


class CacheProvider(Provider):
    """
    Provides caching services using Redis.
    """

    @provide(scope=Scope.APP)
    async def get_cache_service(
        self,
        settings: Settings,
    ) -> AsyncIterator[CacheProtocol]:
        """
        Provides a CacheProtocol implementation.
        """
        redis_client = await redis.from_url(
            str(settings.redis_url),
            encoding="utf-8",
            decode_responses=False,
            retry_on_timeout=True,
            max_connections=50,
            health_check_interval=60,
        )
        cache_service = RedisCacheClient(
            client=redis_client,
            ttl=settings.redis_cache_ttl,
        )

        try:
            await redis_client.ping()
        except Exception as e:
            raise

        try:
            yield cache_service
        finally:
            await cache_service.close()


class UseCaseProvider(Provider):
    """
    Provides application use cases.
    """

    @provide(scope=Scope.REQUEST)
    def get_check_key_in_cache_use_case(
        self,
        cache: CacheProtocol,
    ) -> CheckKeyInCacheUseCase:
        """
        Provides a GetArtifactFromRepoUseCase instance.
        """
        return CheckKeyInCacheUseCase(cache=cache)

    @provide(scope=Scope.REQUEST)
    def add_new_url_to_cache_use_case(
        self,
        cache: CacheProtocol,
    ) -> AddNewUrlToCacheUseCase:
        return AddNewUrlToCacheUseCase(cache=cache)

    @provide(scope=Scope.REQUEST)
    def get_create_uniq_key_use_case(
        self,
        key_generator: RandomKeyGenerator,
        get_check_key_in_cache_use_case: CheckKeyInCacheUseCase,
        add_new_url_to_cache_use_case: AddNewUrlToCacheUseCase,
    ) -> CreateUniqKeyInCacheUseCase:
        """
        Provides a SaveArtifactToRepoUseCase instance.
        """
        return CreateUniqKeyInCacheUseCase(
            key_generator=key_generator,
            check_key_in_cache_uc=get_check_key_in_cache_use_case,
            add_new_url_to_cache_uc=add_new_url_to_cache_use_case,
        )

    @provide(scope=Scope.REQUEST)
    def get_publish_url_to_broker_use_case(
        self,
        message_broker: MessageBrokerPublisherProtocol,
    ) -> PublishUrlToBrokerUseCase:
        """
        Provides a PublishArtifactToBrokerUseCase instance.
        """
        return PublishUrlToBrokerUseCase(
            message_broker=message_broker,
        )

    @provide(scope=Scope.REQUEST)
    def get_create_url_use_case(
        self,
        get_create_uniq_key_use_case: CreateUniqKeyInCacheUseCase,
        get_publish_url_to_broker_use_case: PublishUrlToBrokerUseCase,
    ) -> CreateUrlUseCase:
        """
        Provides a ProcessArtifactUseCase instance.
        """
        return CreateUrlUseCase(
            create_uniq_key_uc=get_create_uniq_key_use_case,
            publish_url_to_broker_uc=get_publish_url_to_broker_use_case,
        )

    @provide(scope=Scope.REQUEST)
    def get_target_url_by_key_use_case(
        self,
        cache: CacheProtocol,
    ) -> GetTargetByKeyUseCase:
        return GetTargetByKeyUseCase(cache=cache)

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
    ) -> RedirectToOriginalUrlUseCase:
        return RedirectToOriginalUrlUseCase(
            get_target_url_by_key_uc=get_target_url_by_key_uc,
            publish_url_to_broker_for_update_uc=get_publish_url_to_broker_uc,
        )

    @provide(scope=Scope.REQUEST)
    def get_user_urls_use_case(
        self,
        uow: UnitOfWorkProtocol
    ) -> GetUserUrlsUseCase:
        """
        Provides a ProcessArtifactUseCase instance.
        """
        return GetUserUrlsUseCase(uow=uow)


PROVIDERS: list[Provider] = [
    SettingsProvider(),
    RandomKeyGeneratorProvider(),
    AuthProvider(),
    CacheProvider(),
    BrokerProvider(),
    DatabaseProvider(),
    RepositoryProvider(),
    UnitOfWorkProvider(),
    ServiceProvider(),
    UseCaseProvider(),
]
