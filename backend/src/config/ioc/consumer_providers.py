from collections.abc import AsyncIterator

import structlog
from dishka import Provider, Scope, provide
from faststream.kafka import KafkaBroker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from src.application.interfaces.broker import MessageBrokerPublisherProtocol
from src.application.interfaces.uow import UnitOfWorkProtocol
from src.application.use_cases.internal.process_new_url import (
    ProcessNewUrlUseCase,
)
from src.application.use_cases.internal.process_url_state_update import (
    UpdateUrlUseCase,
)
from src.config.settings import Settings
from src.infrastructures.broker.publisher import KafkaPublisher
from src.infrastructures.db.repository import SQLAlchemyRepository
from src.infrastructures.db.session import engine_factory, get_session_factory
from src.infrastructures.db.uow import UnitOfWork

__all__ = ("CONSUMER_PROVIDERS",)

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


class RepositoryProvider(Provider):
    """
    Provides repository implementations.
    """

    @provide(scope=Scope.APP)
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

    @provide(scope=Scope.APP)
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

    @provide(scope=Scope.APP)
    def get_message_broker(
        self,
        broker: KafkaBroker,
    ) -> MessageBrokerPublisherProtocol:
        """
        Provides a MessageBrokerPublisherProtocol implementation.
        """
        return KafkaPublisher(broker=broker)


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
    RepositoryProvider(),
    ServiceProvider(),
    SettingsProvider(),
    UseCaseProvider(),
    UnitOfWorkProvider(),
]
