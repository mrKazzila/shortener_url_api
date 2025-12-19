__all__ = ("CacheProtocol",)

from abc import abstractmethod
from typing import Any, Protocol


class CacheProtocol(Protocol):
    @abstractmethod
    async def get(self, key: str) -> dict[str, Any] | None: ...

    @abstractmethod
    async def set(
        self,
        key: str,
        value: dict[str, Any],
        ttl: int | None = None,
    ) -> bool: ...

    @abstractmethod
    async def delete(self, key: str) -> bool: ...

    @abstractmethod
    async def exists(self, key: str) -> bool: ...

    @abstractmethod
    async def clear(self, pattern: str) -> int: ...

    @abstractmethod
    async def set_nx(
        self,
        key: str,
        value: dict[str, Any] | str,
        ttl_seconds: int | None = None,
    ) -> bool: ...
