__all__ = ("COMMON_PROVIDERS",)

from collections.abc import AsyncIterator

import redis.asyncio as redis
import structlog
from dishka import Provider, Scope, provide
from faststream.kafka import KafkaBroker
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from shortener_app.application.interfaces import (
    CacheProtocol,
    MessageBrokerPublisherProtocol,
    RepositoryProtocol,
    UnitOfWorkProtocol,
)
from shortener_app.application.mappers import UrlDtoFacade
from shortener_app.application.mappers.components import (
    UrlCacheToEntityMapper,
    UrlCreatedMapper,
    UrlPublishMapper,
    UrlRedirectedMapper,
    UrlToUserUrlItemMapper,
)
from shortener_app.config.settings import Settings
from shortener_app.infrastructures.broker import (
    KafkaPublisher,
)
from shortener_app.infrastructures.cache import RedisCacheClient
from shortener_app.infrastructures.codecs import (
    PublishUrlJsonCodec,
    UrlCacheRedisHashCodec,
    UrlClickedJsonCodec,
)
from shortener_app.infrastructures.db import (
    SQLAlchemyRepository,
    UnitOfWork,
    engine_factory,
    get_session_factory,
)
from shortener_app.infrastructures.db.mappers import UrlDBMapper
from shortener_app.presentation.mappers import (
    UrlPresentationMapper,
    UserPresentationMapper,
)

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
            bootstrap_servers=[settings.broker_url],
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
            dsn=settings.database_url,
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


class MapperProvider(Provider):
    @provide(scope=Scope.APP)
    def get_url_dto_facade(self) -> UrlDtoFacade:
        return UrlDtoFacade(
            publish_new_url=UrlPublishMapper(),
            created=UrlCreatedMapper(),
            publish_redirected_url=UrlRedirectedMapper(),
            user_item=UrlToUserUrlItemMapper(),
            url_cache_to_entity=UrlCacheToEntityMapper(),
        )

    @provide(scope=Scope.APP)
    def get_url_db_mapper(self) -> UrlDBMapper:
        return UrlDBMapper()

    @provide(scope=Scope.APP)
    def get_url_presentation_mapper(self) -> UrlPresentationMapper:
        return UrlPresentationMapper()

    @provide(scope=Scope.APP)
    def get_user_presentation_mapper(self) -> UserPresentationMapper:
        return UserPresentationMapper()


class CodecProvider(Provider):
    @provide(scope=Scope.APP)
    def get_cache_codec(
        self,
    ) -> UrlCacheRedisHashCodec:
        return UrlCacheRedisHashCodec()

    @provide(scope=Scope.APP)
    def get_message_broker_codec(
        self,
    ) -> PublishUrlJsonCodec:
        return PublishUrlJsonCodec()

    @provide(scope=Scope.APP)
    def get_clicked_url_codec(
        self,
    ) -> UrlClickedJsonCodec:
        return UrlClickedJsonCodec()


class ServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def get_message_broker(
        self,
        broker: KafkaBroker,
        publish_url_codec: PublishUrlJsonCodec,
        url_clicked_codec: UrlClickedJsonCodec,
    ) -> MessageBrokerPublisherProtocol:
        return KafkaPublisher(
            broker=broker,
            publish_url_codec=publish_url_codec,
            url_clicked_codec=url_clicked_codec,
        )


class CacheProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_cache_service(
        self,
        settings: Settings,
    ) -> AsyncIterator[CacheProtocol]:
        redis_client = redis.from_url(
            url=settings.redis_url,
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


COMMON_PROVIDERS: tuple[Provider, ...] = (
    SettingsProvider(),
    MapperProvider(),
    CodecProvider(),
    CacheProvider(),
    BrokerProvider(),
    DatabaseProvider(),
    RepositoryProvider(),
    UnitOfWorkProvider(),
    ServiceProvider(),
)
