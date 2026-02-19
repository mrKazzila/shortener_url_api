__all__ = ("UrlPublishMapper",)

from dataclasses import dataclass
from typing import final

from shortener_app.application.dtos.urls.urls_events import PublishUrlDTO
from shortener_app.application.interfaces.entity_dto_mapper import (
    EntityToDtoMapperProtocol,
)
from shortener_app.domain.entities.url import UrlEntity


@final
@dataclass(frozen=True, slots=True)
class UrlPublishMapper(EntityToDtoMapperProtocol[UrlEntity, PublishUrlDTO]):
    """
    Application policy mapper: UrlEntity -> PublishUrlDTO.

    Used by use-cases that publish URL data externally, keeping Domain free from
    transport/storage formats.
    """

    def to_dto(self, entity: UrlEntity) -> PublishUrlDTO:
        return PublishUrlDTO(
            key=entity.key,
            user_id=entity.user_id,
            target_url=entity.target_url,
        )
