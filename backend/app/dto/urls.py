from dataclasses import dataclass
from typing import NewType

__all__ = (
    "UrlInfoDTO",
    "CreatedUrlDTO",
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
    target_url: str
    key: str
