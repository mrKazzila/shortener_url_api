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
    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return Settings()


class BrokerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_broker(
        self,
        settings: Settings,
    ) -> AsyncIterator[KafkaBroker]:
        broker = KafkaBroker(
            [settings.broker_url],
            enable_idempotence=True,
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
            dsn=settings.database_url,
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
        async with factory() as session:
            yield session


class MapperProvider(Provider):
    @provide(scope=Scope.APP)
    def get_url_mapper(self) -> UrlMapper:
        return UrlMapper()

    @provide(scope=Scope.APP)
    def get_db_mapper(self) -> UrlDBMapper:
        return UrlDBMapper()


class RepositoryProvider(Provider):
    @provide(scope=Scope.APP)
    def get_repository(
        self,
        session: AsyncSession,
        mapper: UrlDBMapper,
    ) -> RepositoryProtocol:
        return SQLAlchemyRepository(
            session=session,
            mapper=mapper,
        )


class UnitOfWorkProvider(Provider):
    @provide(scope=Scope.APP)
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
        mapper: UrlMapper,
    ) -> MessageBrokerPublisherProtocol:
        return KafkaPublisher(
            broker=broker,
            mapper=mapper,
        )


class UseCaseProvider(Provider):
    @provide(scope=Scope.APP)
    def process_new_url_use_case(
        self,
        uow: UnitOfWorkProtocol,
    ) -> ProcessNewUrlUseCase:
        return ProcessNewUrlUseCase(uow=uow)

    @provide(scope=Scope.APP)
    def update_url_use_case(
        self,
        uow: UnitOfWorkProtocol,
    ) -> UpdateUrlUseCase:
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
