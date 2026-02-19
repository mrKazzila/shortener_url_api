__all__ = (
    "UserUrlItemDTO",
    "GetUserUrlsResultDTO",
)

from dataclasses import dataclass
from datetime import datetime
from typing import final


@final
@dataclass(frozen=True, slots=True)
class UserUrlItemDTO:
    """Use-case output item for a single user URL."""

    key: str
    target_url: str
    name: str | None
    clicks_count: int
    is_active: bool
    created_at: datetime
    last_used: datetime | None


@final
@dataclass(frozen=True, slots=True)
class GetUserUrlsResultDTO:
    """Use-case output for the GetUserUrls query."""

    items: list[UserUrlItemDTO]
    count: int
