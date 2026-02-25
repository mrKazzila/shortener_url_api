from dataclasses import dataclass, field

from shortener_app.application.dtos.urls.urls_cache import UrlCacheRecordDTO
from shortener_app.application.dtos.urls.urls_events import PublishUrlDTO
from shortener_app.application.dtos.urls.urls_responses import CreatedUrlDTO
from shortener_app.domain.entities.url import UrlEntity


@dataclass
class SpyUrlDtoFacade:
    return_entity: UrlEntity | None = None
    to_entity_from_cache_calls: list[UrlCacheRecordDTO] = field(
        default_factory=list,
    )

    return_publish_dto: PublishUrlDTO | None = None
    return_created_dto: CreatedUrlDTO | None = None
    to_publish_calls: list[UrlEntity] = field(default_factory=list)
    to_created_calls: list[UrlEntity] = field(default_factory=list)

    def to_entity_from_cache_dto(self, *, dto: UrlCacheRecordDTO) -> UrlEntity:
        self.to_entity_from_cache_calls.append(dto)
        if self.return_entity is None:
            raise RuntimeError("SpyUrlDtoFacade.return_entity is not set")
        return self.return_entity

    def to_publish_dto(self, *, entity: UrlEntity) -> PublishUrlDTO:
        self.to_publish_calls.append(entity)
        if self.return_publish_dto is None:
            raise RuntimeError("SpyUrlDtoFacade.return_publish_dto is not set")
        return self.return_publish_dto

    def to_created_dto(self, *, entity: UrlEntity) -> CreatedUrlDTO:
        self.to_created_calls.append(entity)
        if self.return_created_dto is None:
            raise RuntimeError("SpyUrlDtoFacade.return_created_dto is not set")
        return self.return_created_dto
