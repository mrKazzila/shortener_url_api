__all__ = ("SQLAlchemyRepository",)

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, final
from uuid import UUID

import structlog
from sqlalchemy import (
    Integer,
    String,
    column,
    delete,
    func,
    insert,
    select,
    update,
    values,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from shortener_app.application.interfaces import RepositoryProtocol
from shortener_app.domain.entities import UrlEntity
from shortener_app.infrastructures.db.models import Urls
from shortener_app.infrastructures.db.models.click_inbox import ClickInbox
from shortener_app.infrastructures.mappers import UrlDBMapper

ModelType = TypeVar("ModelType", bound=Urls)

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SQLAlchemyRepository(RepositoryProtocol):
    model: ModelType = Urls
    mapper: UrlDBMapper
    session: AsyncSession

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} for model: {self.model}"

    async def get(  # type: ignore
        self,
        *,
        reference: dict[str, str | int | UUID],
    ) -> UrlEntity | None:
        _statement = select(self.model).filter_by(**reference)
        statement_result = await self.session.execute(statement=_statement)

        if db_model := statement_result.scalar_one_or_none():
            return self.mapper.to_entity(model=db_model)

        return None

    async def get_all(  # type: ignore
        self,
        *,
        reference: dict[str, str | int | UUID],
        limit: int | None = None,
        last_id: int | UUID | None = None,
    ) -> list[UrlEntity]:
        stmt = (
            select(self.model).filter_by(**reference).order_by(self.model.id)
        )

        if last_id is not None:
            stmt = stmt.where(self.model.id > last_id)  # keyset pagination

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

    async def add_bulk(  # type: ignore
        self,
        *,
        entities: list[UrlEntity],
    ) -> None:
        if not entities:
            return

        dicts = [self.mapper.to_model(entity) for entity in entities]
        logger.info(f"ADD BULK: {dicts=!r}")

        stmt = (
            pg_insert(self.model)
            .values(dicts)
            .on_conflict_do_nothing(index_elements=[self.model.key])
        )

        await self.session.execute(stmt)

    async def update(  # type: ignore
        self,
        *,
        entity: UrlEntity,
    ) -> None:
        _statement = (
            update(self.model)
            .where(self.model.key == entity.key)
            .values(
                name=entity.name,
                is_active=entity.is_active,
            )
            .execution_options(synchronize_session=False)
        )
        await self.session.execute(_statement)

    async def delete(  # type: ignore
        self,
        *,
        entity: UrlEntity,
    ) -> None:
        _statement = delete(self.model).where(self.model.key == entity.key)
        await self.session.execute(_statement)

    async def apply_click_events(  # type: ignore
        self,
        *,
        events: list[tuple[UUID, str]],
    ) -> int:
        if not events:
            return 0

        rows = [
            {"event_id": event_id, "url_key": key} for event_id, key in events
        ]

        stmt_ins = (
            pg_insert(ClickInbox)
            .values(rows)
            .on_conflict_do_nothing(index_elements=[ClickInbox.event_id])
            .returning(ClickInbox.url_key)
        )
        stmt_result = await self.session.execute(stmt_ins)
        inserted_keys = list(stmt_result.scalars().all())

        if not inserted_keys:
            return 0

        increments = Counter(inserted_keys)

        await self._increment_clicks_batch(increments=increments)
        return len(inserted_keys)

    async def _increment_clicks_batch(  # type: ignore
        self,
        *,
        increments: Counter[str],
    ) -> None:
        if not increments:
            return

        now = func.now()

        values_ = (
            values(
                column("url_key", String),
                column("cnt", Integer),
                name="v",
            )
            .data(list(increments.items()))
            .alias("v")
        )

        stmt = (
            update(self.model)
            .where(self.model.key == values_.c.url_key)
            .values(
                clicks_count=self.model.clicks_count + values_.c.cnt,
                last_used=now,
            )
        )

        await self.session.execute(stmt)
