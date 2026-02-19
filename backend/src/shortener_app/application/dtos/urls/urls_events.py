__all__ = (
    "PublishUrlDTO",
    "UrlClickedEventDTO",
)

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishUrlDTO:
    key: str
    target_url: str
    user_id: UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class UrlClickedEventDTO:
    """
    Integration event payload published when a short URL is resolved (clicked).

    Used by downstream consumers to update click counters idempotently.
    """

    key: str
    event_id: UUID = field(default_factory=uuid4)
