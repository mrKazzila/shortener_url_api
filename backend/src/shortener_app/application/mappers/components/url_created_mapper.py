__all__ = ("UrlCreatedMapper",)

from dataclasses import dataclass
from typing import final

from shortener_app.application.dtos.urls.urls_responses import CreatedUrlDTO
from shortener_app.application.interfaces.entity_dto_mapper import (
    EntityToDtoMapperProtocol,
)
from shortener_app.domain.entities.url import UrlEntity


@final
@dataclass(frozen=True, slots=True)
class UrlCreatedMapper(EntityToDtoMapperProtocol[UrlEntity, CreatedUrlDTO]):
    """
    Application policy mapper: UrlEntity -> CreatedUrlDTO.
    """

    def to_dto(self, entity: UrlEntity) -> CreatedUrlDTO:
        return CreatedUrlDTO(
            key=entity.key,
            target_url=entity.target_url,
            user_id=entity.user_id,
        )
