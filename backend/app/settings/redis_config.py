from redis.asyncio import Redis
from app.settings.config import settings

_redis: Redis | None = None

async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(
            str(settings.redis_url),
            decode_responses=False,
            max_connections=30,
            socket_keepalive=True,
            health_check_interval=30,
            retry_on_timeout=True,
        )
    return _redis

async def close_redis():
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None
