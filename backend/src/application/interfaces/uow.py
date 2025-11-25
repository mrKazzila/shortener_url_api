from abc import abstractmethod
from typing import Protocol, Self

__all__ = ("UnitOfWorkProtocol",)

from src.application.interfaces.repository import RepositoryProtocol


class UnitOfWorkProtocol(Protocol):
    repository: RepositoryProtocol

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool | None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
