from dataclasses import dataclass

__all__ = (
    "UrlInfoDTO",
    "CreatedUrlDTO",
)


@dataclass(frozen=True, slots=True)
class UrlInfoDTO:
    id: int
    target_url: str
    is_active: bool
    clicks_count: int


@dataclass(frozen=True, slots=True)
class CreatedUrlDTO:
    target_url: str
    key: str
