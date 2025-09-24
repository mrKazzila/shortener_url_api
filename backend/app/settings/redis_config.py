from redis.asyncio import Redis

from app.settings.config import settings

_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(
            str(settings.redis_url),
            decode_responses=True,
            max_connections=100,
        )
    return _redis
