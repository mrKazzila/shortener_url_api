from uuid import UUID

from app.adapters import UrlsRepository
from app.dto.urls import DBUrlDTO
from app.service_layer.cqrs.query.abc_query import ABCQueryService

__all__ = ("QueryService",)


class QueryService(ABCQueryService):
    async def get_url_by_key(self, *, url_key: str) -> DBUrlDTO | None:
        return await self._get_url(reference={"key": url_key})

    async def get_url_by_user(self, *, user_id: UUID) -> DBUrlDTO | None:
        return await self._get_url(reference={"user_id": str(user_id)})

    async def get_all_user_urls(
        self,
        *,
        user_id: UUID,
        pagination_data: dict[str, int | None],
    ) -> list[DBUrlDTO]:
        return await self._get_all_url(
            user_id=user_id,
            pagination_data=pagination_data,
        )

    async def _get_url(
        self,
        *,
        reference: dict[str, str | int | UUID | bool | None],
    ) -> DBUrlDTO | None:
        async with self.session_factory() as session:
            if not (
                url := await UrlsRepository(session=session).get(
                    reference=reference,
                )
            ):
                return None

            return DBUrlDTO(
                id=url.id,
                user_id=url.user_id,
                key=url.key,
                target_url=url.target_url,
                name=url.name,
                clicks_count=url.clicks_count,
                is_active=url.is_active,
                created_at=url.created_at,
                last_used=url.last_used,
            )

    async def _get_all_url(
        self,
        *,
        user_id: UUID,
        pagination_data: dict[str, int | None],
    ) -> list[DBUrlDTO]:
        async with self.session_factory() as session:
            if not (
                urls := await UrlsRepository(session=session).get_all(
                    user_id=user_id,
                    **pagination_data,
                )
            ):
                return []

            return [
                DBUrlDTO(
                    id=url.id,
                    user_id=url.user_id,
                    key=url.key,
                    target_url=url.target_url,
                    name=url.name,
                    clicks_count=url.clicks_count,
                    is_active=url.is_active,
                    created_at=url.created_at,
                    last_used=url.last_used,
                )
                for url in urls
            ]
