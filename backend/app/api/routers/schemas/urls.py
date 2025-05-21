from datetime import datetime

from pydantic import BaseModel

__all__ = ("SReturnUrl", "SUserUrl", "SUserUrls")


class SReturnUrl(BaseModel):
    """Base URL schema."""

    key: str
    target_url: str


class SUserUrl(BaseModel):
    """User URL."""

    key: str
    target_url: str
    name: str | None = None
    clicks_count: int
    is_active: bool = True
    created_at: datetime
    last_used: datetime | None = None


class SUserUrls(BaseModel):
    """User URLs."""

    count: int
    urls: list[SUserUrl] | None
