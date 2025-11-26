__all__ = (
    "SUserUrl",
    "SUserUrls",
)

from datetime import datetime
from typing import final

from pydantic import BaseModel


@final
class SUserUrl(BaseModel):
    """User URL."""

    key: str
    target_url: str
    name: str | None = None
    clicks_count: int
    is_active: bool = True
    created_at: datetime
    last_used: datetime | None = None


@final
class SUserUrls(BaseModel):
    """User URLs."""

    count: int
    urls: list[SUserUrl] | None
