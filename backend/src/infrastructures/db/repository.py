from collections import Counter
from datetime import datetime
from typing import TypeVar
from uuid import UUID

from sqlalchemy import func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repository import RepositoryProtocol
from src.domain.entities import UrlEntity
from src.infrastructures._mappers.url_db_mapper import UrlDBMapper
from src.infrastructures.db.models import Urls

ModelType = TypeVar("ModelType", bound=Urls)


class SQLAlchemyRepository(RepositoryProtocol):
    __slots__ = ("session",)
    model = Urls

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session
        self.mapper = UrlDBMapper()  # TODO: to clacc

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} for model: {self.model}"

    async def get(  # type: ignore
        self,
        *,
        reference: dict[str, str | int | UUID],
    ) -> ModelType | None:
        _statement = select(self.model).filter_by(**reference)
        statement_result = await self.session.execute(statement=_statement)

        return statement_result.scalar_one_or_none()

    async def get_all(  # type: ignore
        self,
        *,
        reference: dict[str, str | int | UUID],
        limit: int | None = None,
        skip: int | None = None,
        offset: int | None = None,
    ) -> list[UrlEntity]:
        actual_offset = skip if skip is not None else offset

        stmt = select(self.model).filter_by(**reference)

        if actual_offset is not None:
            stmt = stmt.offset(actual_offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def add(  # type: ignore
        self,
        *,
        data: dict[str, str | int | UUID | bool | datetime],
    ) -> None:
        _statement = insert(self.model).values(**data)
        await self.session.execute(statement=_statement)

    async def update(  # type: ignore
        self,
        *,
        reference: dict[str, str | int | UUID],
        **update_data: str | int | datetime | bool,
    ) -> None:
        _statement = (
            update(self.model).filter_by(**reference).values(**update_data)
        )
        await self.session.execute(_statement)

    async def increment_clicks(  # type: ignore
        self,
        *,
        key: str,
    ) -> None:
        _statement = (
            update(self.model)
            .where(self.model.key == key)
            .values(
                clicks_count=self.model.clicks_count + 1,
                last_used=func.now(),
            )
        )
        await self.session.execute(_statement)

    async def increment_clicks_batch(  # type: ignore
        self,
        *,
        increments: Counter[str],
    ) -> None:
        now = func.now()

        for key, amount in increments.items():
            stmt = (
                update(self.model)
                .where(self.model.key == key)
                .values(
                    clicks_count=self.model.clicks_count + amount,
                    last_used=now,
                )
            )
            await self.session.execute(stmt)

    async def add_bulk(  # type: ignore
        self,
        *,
        entities: list[UrlEntity],
    ) -> None:
        db_objects = [self.mapper.to_model(entity) for entity in entities]
        stmt = insert(self.model).values([obj.__dict__ for obj in db_objects])

        await self.session.execute(stmt)
