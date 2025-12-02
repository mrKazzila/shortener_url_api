__all__ = (
    "GetUserUrlsDTO",
    "PaginationDTO",
    "XUserHeaderDTO",
)

from dataclasses import dataclass
from typing import final
from uuid import UUID


@final
@dataclass(frozen=True, slots=True)
class XUserHeaderDTO:
    x_user_id: str | None


@final
@dataclass(frozen=True, slots=True)
class GetUserUrlsDTO:
    user_id: UUID
    pagination_data: "PaginationDTO"


@final
@dataclass(frozen=True, slots=True)
class PaginationDTO:
    limit: int = 10
    last_id: int | None = None
