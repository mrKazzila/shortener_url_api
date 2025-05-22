from sqlalchemy import func, select, update
from sqlalchemy.orm import Mapped

from app.adapters.base import SQLAlchemyRepository
from app.models import Urls

__all__ = ("UrlsRepository",)


class UrlsRepository(SQLAlchemyRepository):
    """Urls repository with optimized methods for click tracking."""

    model = Urls

    async def increment_clicks_and_return(self, *, key: str) -> Urls | None:
        """Increment clicks and return updated URL in one transaction."""
        if not (url := await self._get_by_key_with_lock(key=key)):
            return None

        await self._increment_clicks(url_id=url.id)
        await self.session.commit()
        return url

    async def _get_by_key_with_lock(self, *, key: str) -> Urls | None:
        """Get URL by key with lock for update."""
        stmt = (
            select(self.model).where(self.model.key == key).with_for_update()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _increment_clicks(self, *, url_id: Mapped[int]) -> None:
        """Atomically increment clicks counter."""
        stmt = (
            update(self.model)
            .where(self.model.id == url_id)
            .values(
                clicks_count=self.model.clicks_count + 1,
                last_used=func.now(),
            )
        )
        await self.session.execute(stmt)
