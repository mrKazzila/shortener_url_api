from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Self, final
from uuid import UUID


__all__ = (
    "CreateUrlDTO",
    "CreatedUrlDTO",
    # "ClickedUrlDTO",
    # "DBUrlDTO",
    "PublishUrlDTO",
    # "UrlInfoDTO",
)


# @final
# @dataclass(frozen=True, slots=True, kw_only=True)
# class UrlInfoDTO:
#     id: int
#     target_url: str
#     is_active: bool
#     clicks_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUrlDTO:
    target_url: str
    user_id: UUID

    def to_dict(self: Self) -> dict[str, str | UUID]:
        return asdict(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatedUrlDTO(CreateUrlDTO):
    key: str

    def to_dict(self: Self) -> dict[str, str | UUID]:
        return asdict(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishUrlDTO(CreatedUrlDTO):
    # For Kafka
    def to_dict(self: Self) -> dict[str, str | UUID]:
        return asdict(self)


# @final
# @dataclass(frozen=True, slots=True, kw_only=True)
# class ClickedUrlDTO:
#     key: str
#     target_url: str
#     clicks_count: int

#
# @final
# @dataclass(frozen=True, slots=True, kw_only=True)
# class DBUrlDTO:
#     id: int
#     user_id: UUID
#     key: str
#     target_url: str
#     name: str | None
#     clicks_count: int
#     is_active: bool
#     created_at: datetime
#     last_used: datetime
#
#     def to_dict(self: Self) -> dict[str, str | UUID]:
#         return asdict(self)
