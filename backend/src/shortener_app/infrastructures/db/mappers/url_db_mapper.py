__all__ = ("UrlDBMapper",)

from dataclasses import dataclass
from typing import final

from shortener_app.domain.entities.url import UrlEntity
from shortener_app.infrastructures.db.models import Urls


@final
@dataclass(frozen=True, slots=True)
class UrlDBMapper:
    """
    Infrastructure persistence mapper: ORM model <-> Domain entity.

    Responsibilities:
    - Translate database/ORM representation (Urls model) into a Domain UrlEntity.
    - Translate Domain UrlEntity into persistence data suitable for ORM insert/update.

    Notes:
    - This mapper belongs to the Infrastructure layer because it depends on ORM models.
    - No DTOs here: keep transport concerns out of persistence mapping.
    """

    @staticmethod
    def to_entity(model: Urls) -> UrlEntity:
        """Convert an ORM Urls model instance into a Domain UrlEntity."""
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
    def to_model_data(entity: UrlEntity) -> dict:
        """
        Convert a Domain UrlEntity into a dict of fields suitable for ORM persistence.

        Returned dict is intended to be used with ORM constructors or update operations.
        """
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
