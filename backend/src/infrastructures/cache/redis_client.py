__all__ = ("RedisCacheClient",)

import json
from dataclasses import dataclass
from typing import Any, final

import redis.exceptions
import structlog
from redis.asyncio import Redis

from src.application.interfaces import CacheProtocol

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class RedisCacheClient(CacheProtocol):
    client: Redis
    ttl: int | None = None  # default TTL in seconds

    async def get(self, key: str) -> dict[str, Any] | None:
        """Get a value by key and deserialize JSON."""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (redis.exceptions.RedisError, json.JSONDecodeError) as e:
            logger.error("Redis get operation failed", key=key, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: dict[str, Any] | str,
        ttl: int | None = None,
    ) -> bool:
        """
        Set a key-value pair. Supports dict (serialized to JSON) or str.
        TTL can be overridden per call.
        """
        try:
            serialized = (
                json.dumps(value) if isinstance(value, dict) else str(value)
            )
            expire = ttl or self.ttl
            if expire:
                await self.client.setex(key, expire, serialized)
            else:
                await self.client.set(key, serialized)
            return True
        except (redis.exceptions.RedisError, TypeError, ValueError) as e:
            logger.error(
                "Redis set operation failed",
                key=key,
                value=value,
                error=str(e),
            )
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(await self.client.exists(key))
        except redis.exceptions.RedisError as e:
            logger.error(
                "Redis exists operation failed",
                key=key,
                error=str(e),
            )
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key from Redis."""
        try:
            return bool(await self.client.delete(key))
        except redis.exceptions.RedisError as e:
            logger.error(
                "Redis delete operation failed",
                key=key,
                error=str(e),
            )
            return False

    async def clear(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        try:
            keys = [key async for key in self.client.scan_iter(match=pattern)]
            if keys:
                deleted_count = await self.client.delete(*keys)
                logger.info(
                    "Cleared keys matching pattern",
                    pattern=pattern,
                    count=deleted_count,
                )
                return deleted_count
            return 0
        except redis.exceptions.RedisError as e:
            logger.error(
                "Redis clear operation failed",
                pattern=pattern,
                error=str(e),
            )
            return 0

    async def close(self) -> None:
        """Close the Redis connection."""
        try:
            await self.client.close()
            logger.info("Redis connection closed")
        except redis.exceptions.RedisError as e:
            logger.error("Failed to close Redis connection", error=str(e))

    async def set_nx(
        self,
        key: str,
        value: dict[str, Any] | str,
        ttl_seconds: int | None = None,
    ) -> bool:
        try:
            serialized = (
                json.dumps(value, ensure_ascii=False)
                if isinstance(value, dict)
                else str(value)
            )
            expire = ttl_seconds if ttl_seconds is not None else self.ttl

            ok = await self.client.set(
                key,
                serialized,
                nx=True,
                ex=expire,
            )
            return bool(ok)
        except (redis.exceptions.RedisError, TypeError, ValueError) as e:
            logger.error(
                "Redis set_nx operation failed",
                key=key,
                error=str(e),
            )
            return False
