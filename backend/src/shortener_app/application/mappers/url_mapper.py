__all__ = ("UrlMapper",)

from dataclasses import dataclass
from typing import final
from uuid import UUID

from shortener_app.application.dtos.urls import PublishUrlDTO
from shortener_app.domain.entities.url import UrlEntity


@final
@dataclass(frozen=True, slots=True)
class UrlMapper:
    @staticmethod
    def to_publish_dto(entity: UrlEntity) -> PublishUrlDTO:
        return PublishUrlDTO(
            key=entity.key,
            user_id=str(entity.user_id),
            target_url=entity.target_url,
        )

    @staticmethod
    def to_cache_dict(entity: UrlEntity) -> dict[str, str]:
        return {
            "target_url": entity.target_url,
            "user_id": str(entity.user_id),
        }

    @staticmethod
    def to_entity(cache: dict[str, str]) -> UrlEntity:
        return UrlEntity.create(
            user_id=UUID(cache["user_id"]),
            target_url=cache["target_url"],
            key=cache["key"],
        )
