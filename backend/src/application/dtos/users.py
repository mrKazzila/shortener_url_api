from dataclasses import dataclass
from typing import final
from uuid import UUID

__all__ = (
    "GetUserUrlsDTO",
    "PaginationDTO",
    "XUserHeaderDTO",
)


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
    limit: int = 0
    skip: int = 0
    offset: int = 0
