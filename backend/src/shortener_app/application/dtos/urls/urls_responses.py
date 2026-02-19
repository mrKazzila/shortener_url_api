__all__ = ("CreatedUrlDTO",)

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatedUrlDTO:
    key: str
    target_url: str
    user_id: UUID
