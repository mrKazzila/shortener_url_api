from dataclasses import asdict, dataclass
from datetime import datetime
from typing import NewType, Self
from uuid import UUID

__all__ = (
    "CreatedUrlDTO",
    "ClickedUrlDTO",
    "DBUrlDTO",
    "UrlDTO",
    "UrlInfoDTO",
    "XUserHeader",
)


XUserHeader = NewType("XUserHeader", str)


@dataclass(frozen=True, slots=True, kw_only=True)
class UrlInfoDTO:
    id: int
    target_url: str
    is_active: bool
    clicks_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatedUrlDTO:
    user_id: UUID
    target_url: str
    key: str

    def to_dict(self: Self) -> dict[str, str | UUID]:
        return asdict(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class UrlDTO:
    target_url: str
    user_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class ClickedUrlDTO:
    key: str
    target_url: str
    clicks_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class DBUrlDTO:
    id: int
    user_id: UUID
    key: str
    target_url: str
    name: str | None
    clicks_count: int
    is_active: bool
    created_at: datetime
    last_used: datetime

    def to_dict(self: Self) -> dict[str, str | UUID]:
        return asdict(self)
