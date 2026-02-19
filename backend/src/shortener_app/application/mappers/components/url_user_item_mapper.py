__all__ = ("UrlToUserUrlItemMapper",)

from dataclasses import dataclass
from typing import final

from shortener_app.application.dtos.users.user_responses import UserUrlItemDTO
from shortener_app.application.interfaces.entity_dto_mapper import (
    EntityToDtoMapperProtocol,
)
from shortener_app.domain.entities.url import UrlEntity


@final
@dataclass(frozen=True, slots=True)
class UrlToUserUrlItemMapper(
    EntityToDtoMapperProtocol[UrlEntity, UserUrlItemDTO],
):
    """
    Application policy mapper: UrlEntity -> UserUrlItemDTO.

    Converts Domain entities into use-case output DTOs, so Presentation does not
    depend on Domain objects.
    """

    def to_dto(self, entity: UrlEntity) -> UserUrlItemDTO:
        return UserUrlItemDTO(
            key=entity.key,
            target_url=entity.target_url,
            name=entity.name,
            clicks_count=entity.clicks_count,
            is_active=entity.is_active,
            created_at=entity.created_at,
            last_used=entity.last_used,
        )
