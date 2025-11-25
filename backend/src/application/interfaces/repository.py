from abc import abstractmethod
from collections import Counter
from datetime import datetime
from typing import Protocol
from uuid import UUID

from src.domain.entities.url import UrlEntity

__all__ = ("RepositoryProtocol",)


class RepositoryProtocol(Protocol):

    @abstractmethod
    async def get(
        self,
        *,
        reference: dict[str, str | int | UUID]
    ) -> UrlEntity | None:
        ...

    @abstractmethod
    async def get_all(
        self,
        *,
        reference: dict[str, str | int | UUID],
        limit: int | None = None,
        skip: int | None = None,
        offset: int | None = None,
    ) -> list[UrlEntity]:
        ...

    @abstractmethod
    async def add(
        self,
        *,
        data: UrlEntity,
    ) -> None:
        ...

    @abstractmethod
    async def add_bulk(
        self,
        *,
        entities: list[UrlEntity],
    ):
        ...

    @abstractmethod
    async def update(
        self,
        *,
        reference: dict[str, str | int | UUID],
        **update_data: str | int | datetime | bool,
    ) -> None:
        ...

    @abstractmethod
    async def increment_clicks(
        self,
        *,
        key: str,
    ) -> None:
        ...

    @abstractmethod
    async def increment_clicks_batch(
        self,
        *,
        increments: Counter[str],
    ) -> None:
        ...
