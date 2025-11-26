__all__ = ("UrlDBMapper",)

from dataclasses import dataclass
from typing import final

from src.domain.entities.url import UrlEntity
from src.infrastructures.db.models import Urls


@final
@dataclass(frozen=True, slots=True)
class UrlDBMapper:
    @staticmethod
    def to_entity(model: Urls) -> UrlEntity:
        return UrlEntity(
            id=model.id,
            user_id=model.user_id,
            key=model.key,
            target_url=model.target_url,
            name=model.name,
            is_active=model.is_active,
            clicks_count=model.clicks_count,
            created_at=model.created_at,
            last_used=model.last_used,
        )

    @staticmethod
    def to_model(entity: UrlEntity) -> dict:
        return {
            "user_id": str(entity.user_id),
            "key": entity.key,
            "target_url": entity.target_url,
            "name": entity.name,
            "clicks_count": entity.clicks_count,
            "is_active": entity.is_active,
            "created_at": entity.created_at,
            "last_used": entity.last_used,
        }
