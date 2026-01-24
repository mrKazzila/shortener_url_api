__all__ = (
    "CreateUrlDTO",
    "CreatedUrlDTO",
    "DeleteUrlDTO",
    "PublishUrlDTO",
    "UpdateUrlDTO",
)

from dataclasses import asdict, dataclass
from typing import Self
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUrlDTO:
    target_url: str
    user_id: UUID

    def to_dict(self: Self) -> dict[str, str | UUID]:
        data = asdict(self)
        if isinstance(data.get("user_id"), UUID):
            data["user_id"] = str(data["user_id"])
        return data


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatedUrlDTO(CreateUrlDTO):
    key: str

    def to_dict(self: Self) -> dict[str, str | UUID]:
        return asdict(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishUrlDTO(CreatedUrlDTO):
    user_id: str

    def to_dict(self: Self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteUrlDTO:
    key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateUrlDTO:
    key: str
    name: str | None = None
    is_active: bool | None = None
