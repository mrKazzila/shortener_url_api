__all__ = ("RepositoryProtocol",)

from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from src.domain.entities.url import UrlEntity


class RepositoryProtocol(Protocol):
    @abstractmethod
    async def get(
        self,
        *,
        reference: dict[str, str | int | UUID],
    ) -> UrlEntity | None: ...

    @abstractmethod
    async def get_all(
        self,
        *,
        reference: dict[str, str | int | UUID],
        limit: int | None = None,
        last_id: int | UUID | None = None,
    ) -> list[UrlEntity]: ...

    @abstractmethod
    async def add(
        self,
        *,
        data: UrlEntity,
    ) -> None: ...

    @abstractmethod
    async def add_bulk(
        self,
        *,
        entities: list[UrlEntity],
    ): ...

    @abstractmethod
    async def update(
        self,
        *,
        entity: UrlEntity,
    ) -> None: ...

    @abstractmethod
    async def delete(
        self,
        *,
        entity: UrlEntity,
    ) -> None: ...

    @abstractmethod
    async def apply_click_events(
        self,
        *,
        events: list[tuple[UUID, str]],
    ) -> int: ...
