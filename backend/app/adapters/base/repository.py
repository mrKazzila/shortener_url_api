from datetime import datetime
from typing import TypeVar
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.base import ABCRepository
from app.models import Base

__all__ = ("SQLAlchemyRepository",)

ModelType = TypeVar("ModelType", bound=Base)


class SQLAlchemyRepository(ABCRepository):
    __slots__ = ("session",)
    model: type[ModelType] = None

    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} for model: {self.model}"

    async def add(
        self,
        *,
        data: dict[str, str | int | UUID | bool | datetime],
    ) -> None:
        """Add new entity."""
        _statement = insert(self.model).values(**data)
        await self.session.execute(statement=_statement)

    async def get(
        self,
        *,
        reference: dict[str, str | int | UUID],
    ) -> type(model) | None:
        """Get entity by some reference."""
        _statement = select(self.model).filter_by(**reference)
        statement_result = await self.session.execute(statement=_statement)

        return statement_result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        user_id: UUID,
        limit: int | None = None,
        skip: int | None = None,
        offset: int | None = None,
    ) -> list[type(model)]:
        """Get all entities for a specific user with pagination support."""
        actual_offset = skip if skip is not None else offset

        _statement = select(self.model).filter_by(user_id=user_id)

        if actual_offset is not None:
            _statement = _statement.offset(actual_offset)
        if limit is not None:
            _statement = _statement.limit(limit)

        result = await self.session.execute(_statement)
        return list(result.scalars().all())

    async def update(
        self,
        *,
        model_id: int,
        **update_data: str | int | datetime | bool,
    ) -> None:
        """Update entity some data."""
        _statement = (
            update(self.model).filter_by(id=model_id).values(**update_data)
        )
        await self.session.execute(_statement)
