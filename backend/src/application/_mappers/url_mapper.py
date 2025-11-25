from src.application.dtos.urls import PublishUrlDTO
from src.domain.entities.url import UrlEntity


class UrlMapper:
    @staticmethod
    def to_publish_dto(entity: UrlEntity) -> PublishUrlDTO:
        return PublishUrlDTO(
            key=entity.key,
            user_id=entity.user_id,
            target_url=entity.target_url,
        )

    @staticmethod
    def to_cache_dict(entity: UrlEntity) -> dict:
        return {
            "target_url": entity.target_url,
            "user_id": str(entity.user_id),
        }
