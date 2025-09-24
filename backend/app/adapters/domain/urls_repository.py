from sqlalchemy import func, update
from sqlalchemy.orm import Mapped

from app.adapters.base import SQLAlchemyRepository
from app.models import Urls

__all__ = ("UrlsRepository",)


class UrlsRepository(SQLAlchemyRepository):
    """Urls repository with optimized methods for click tracking."""

    model = Urls

    async def increment_clicks(self, *, url_id: Mapped[int]) -> None:
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
