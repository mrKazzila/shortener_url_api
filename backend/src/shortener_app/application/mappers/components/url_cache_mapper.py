__all__ = ("UrlCacheToEntityMapper",)

from dataclasses import dataclass
from typing import final

from shortener_app.application.dtos.urls.urls_cache import UrlCacheRecordDTO
from shortener_app.application.interfaces.entity_dto_mapper import (
    DtoToEntityMapperProtocol,
)
from shortener_app.domain.entities.url import UrlEntity


@final
@dataclass(frozen=True, slots=True)
class UrlCacheToEntityMapper(
    DtoToEntityMapperProtocol[UrlCacheRecordDTO, UrlEntity],
):
    """
    Application policy mapper: UrlCacheRecordDTO -> UrlEntity
    """

    def to_entity(self, dto: UrlCacheRecordDTO) -> UrlEntity:
        return UrlEntity.create(
            key=dto.key,
            user_id=dto.user_id,
            target_url=dto.target_url,
            name=dto.name,
        )
