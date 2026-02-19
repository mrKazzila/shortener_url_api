__all__ = (
    "UrlCacheSeedDTO",
    "UrlCacheRecordDTO",
)

from dataclasses import dataclass
from typing import final
from uuid import UUID


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UrlCacheSeedDTO:
    """
    Application DTO used as input for cache-related operations where the key
    is not yet allocated (e.g., key generation with SETNX).
    """

    target_url: str
    user_id: UUID
    name: str | None = None
    is_active: bool = True


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UrlCacheRecordDTO:
    """
    Cache record DTO with an allocated key.

    This DTO represents a storage-friendly snapshot that is safe to serialize
    and store in Redis.
    """

    key: str
    target_url: str
    user_id: UUID
    name: str | None = None
    is_active: bool = True
