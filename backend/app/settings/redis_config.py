import logging

from redis.asyncio import ConnectionPool, Redis

from app.settings.config import settings

__all__ = ("get_redis",)

logger = logging.getLogger(__name__)


class RedisConnection:
    def __init__(self):
        self.pool: ConnectionPool | None = None

    async def init_pool(self):
        logger.debug("Initializing Redis connection pool")
        self.pool = ConnectionPool.from_url(
            str(settings.redis_url),
            decode_responses=True,
            max_connections=10,
        )

    async def get_connection(self) -> Redis:
        if not self.pool:
            await self.init_pool()
        return Redis(connection_pool=self.pool)

    async def close(self):
        if self.pool:
            await self.pool.disconnect()


redis_connection = RedisConnection()


async def get_redis() -> Redis:
    return await redis_connection.get_connection()
