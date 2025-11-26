__all__ = ("UrlEntity",)

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import final
from uuid import UUID

from src.domain.exceptions.domain import ValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UrlEntity:
    id: int

    user_id: UUID
    name: str | None = None

    key: str
    target_url: str

    is_active: bool = True

    clicks_count: int = 0

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_used: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """
        Validates business invariants of the UrlEntity.

        Domain entities must protect their invariants and ensure
        that invalid state cannot exist in the domain model.

        Raises:
            ValidationError: If any business invariant is violated.
        """
        if self.created_at > datetime.now(UTC):
            raise ValidationError("Acquisition date cannot be in the future")

        if self.last_used < self.created_at:
            raise ValidationError(
                "last_used cannot be earlier than created_at",
            )

        if len(self.key) != 5:
            raise ValidationError("Key must be exactly 5 characters long")

        if self.clicks_count < 0:
            raise ValidationError(
                "Description must be at most 1000 characters",
            )

    @classmethod
    def create(
        cls,
        *,
        user_id: UUID,
        target_url: str,
        key: str,
        name: str | None = None,
    ) -> "UrlEntity":
        return cls(
            id=0,
            user_id=user_id,
            key=key,
            target_url=target_url,
            name=name,
        )
