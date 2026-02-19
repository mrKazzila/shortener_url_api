__all__ = (
    "CreateUrlDTO",
    "DeleteUrlDTO",
    "UpdateUrlDTO",
)

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUrlDTO:
    target_url: str
    user_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteUrlDTO:
    key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateUrlDTO:
    key: str
    name: str | None = None
    is_active: bool | None = None
