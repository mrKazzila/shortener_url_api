__all__ = ("UrlRedirectedMapper",)

from dataclasses import dataclass
from typing import final

from shortener_app.application.dtos.urls.urls_events import UrlClickedEventDTO
from shortener_app.application.interfaces.entity_dto_mapper import (
    EntityToDtoMapperProtocol,
)
from shortener_app.domain.entities.url import UrlEntity


@final
@dataclass(frozen=True, slots=True)
class UrlRedirectedMapper(
    EntityToDtoMapperProtocol[UrlEntity, UrlClickedEventDTO],
):
    """
    Application policy mapper: UrlEntity -> UrlClickedEventDTO.
    """

    def to_dto(self, entity: UrlEntity) -> UrlClickedEventDTO:
        return UrlClickedEventDTO(key=entity.key)
