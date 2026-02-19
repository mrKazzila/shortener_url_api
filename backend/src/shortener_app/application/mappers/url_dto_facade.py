__all__ = ("UrlDtoFacade",)

from dataclasses import dataclass
from typing import final

from shortener_app.application.dtos.urls.urls_cache import UrlCacheRecordDTO
from shortener_app.application.dtos.urls.urls_events import (
    PublishUrlDTO,
    UrlClickedEventDTO,
)
from shortener_app.application.dtos.urls.urls_responses import CreatedUrlDTO
from shortener_app.application.dtos.users.user_responses import UserUrlItemDTO
from shortener_app.application.mappers.components import (
    UrlCacheToEntityMapper,
    UrlCreatedMapper,
    UrlPublishMapper,
    UrlRedirectedMapper,
    UrlToUserUrlItemMapper,
)
from shortener_app.domain.entities.url import UrlEntity


@final
@dataclass(frozen=True, slots=True)
class UrlDtoFacade:
    """
    Facade over URL-related mappers.

    Purpose:
    - Keep use-cases from depending on multiple mapper objects.
    - Provide explicit, typed conversion methods per DTO.
    """

    publish_new_url: UrlPublishMapper
    created: UrlCreatedMapper
    publish_redirected_url: UrlRedirectedMapper
    url_cache_to_entity: UrlCacheToEntityMapper
    user_item: UrlToUserUrlItemMapper

    def to_publish_dto(self, entity: UrlEntity) -> PublishUrlDTO:
        return self.publish_new_url.to_dto(entity)

    def to_created_dto(self, entity: UrlEntity) -> CreatedUrlDTO:
        return self.created.to_dto(entity)

    def to_user_url_item_dto(self, entity: UrlEntity) -> UserUrlItemDTO:
        return self.user_item.to_dto(entity)

    def to_publish_redirected_dto(
        self,
        entity: UrlEntity,
    ) -> UrlClickedEventDTO:
        return self.publish_redirected_url.to_dto(entity)

    def to_entity_from_cache_dto(self, dto: UrlCacheRecordDTO) -> UrlEntity:
        return self.url_cache_to_entity.to_entity(dto)
