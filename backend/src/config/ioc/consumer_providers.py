__all__ = ("CONSUMER_PROVIDERS",)

from collections.abc import AsyncIterator

import structlog
from dishka import Provider, Scope, provide
from faststream.kafka import KafkaBroker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from src.application.interfaces import (
    MessageBrokerPublisherProtocol,
    RepositoryProtocol,
    UnitOfWorkProtocol,
)
from src.application.mappers import UrlMapper
from src.application.use_cases.internal import (
    ProcessNewUrlUseCase,
    UpdateUrlUseCase,
)
from src.config.settings import Settings
from src.infrastructures.broker import KafkaPublisher
from src.infrastructures.db import (
    SQLAlchemyRepository,
    UnitOfWork,
    engine_factory,
    get_session_factory,
)
from src.infrastructures.mappers import UrlDBMapper

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
                queue=settings.broker_new_artifact_queue,
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

    @provide(scope=Scope.APP)
    async def get_session(
        self,
        factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        """
        Provides an asynchronous SQLAlchemy session.
        """
        async with factory() as session:
            yield session


class MapperProvider(Provider):
    """
    Provides various mapper implementations for different layers.
    """

    @provide(scope=Scope.APP)
    def get_url_mapper(self) -> UrlMapper:
        return UrlMapper()

    @provide(scope=Scope.APP)
    def get_db_mapper(self) -> UrlDBMapper:
        return UrlDBMapper()


class RepositoryProvider(Provider):
    """
    Provides repository implementations.
    """

    @provide(scope=Scope.APP)
    def get_repository(
        self,
        session: AsyncSession,
        mapper: UrlDBMapper,
    ) -> RepositoryProtocol:
        """
        Provides an ArtifactRepositoryProtocol implementation.
        """
        return SQLAlchemyRepository(
            session=session,
            mapper=mapper,
        )


class UnitOfWorkProvider(Provider):
    """
    Provides Unit of Work implementations.
    """

    @provide(scope=Scope.APP)
    def get_unit_of_work(
        self,
        session: AsyncSession,
        repository: RepositoryProtocol,
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

    @provide(scope=Scope.APP)
    def get_message_broker(
        self,
        broker: KafkaBroker,
        mapper: UrlMapper,
    ) -> MessageBrokerPublisherProtocol:
        """
        Provides a MessageBrokerPublisherProtocol implementation.
        """
        return KafkaPublisher(
            broker=broker,
            mapper=mapper,
        )


class UseCaseProvider(Provider):
    """
    Provides application use cases.
    """

    @provide(scope=Scope.APP)
    def process_new_url_use_case(
        self,
        uow: UnitOfWorkProtocol,
    ) -> ProcessNewUrlUseCase:
        """
        Provides a GetArtifactFromRepoUseCase instance.
        """
        return ProcessNewUrlUseCase(uow=uow)

    @provide(scope=Scope.APP)
    def update_url_use_case(
        self,
        uow: UnitOfWorkProtocol,
    ) -> UpdateUrlUseCase:
        """
        Provides a GetArtifactFromRepoUseCase instance.
        """
        return UpdateUrlUseCase(uow=uow)


CONSUMER_PROVIDERS: list[Provider] = [
    BrokerProvider(),
    DatabaseProvider(),
    MapperProvider(),
    RepositoryProvider(),
    ServiceProvider(),
    SettingsProvider(),
    UseCaseProvider(),
    UnitOfWorkProvider(),
]
