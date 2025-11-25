__all__ = ("UserPresentationMapper",)

from dataclasses import dataclass
from typing import final

from src.domain.entities.url import UrlEntity
from src.presentation.api.schemas.users import SUserUrl, SUserUrls


@final
@dataclass(frozen=True, slots=True)
class UserPresentationMapper:
    @staticmethod
    def to_response(user_urls: list["UrlEntity"]) -> SUserUrls:
        return SUserUrls(
            count=len(user_urls),
            urls=[
                SUserUrl(
                    key=url.key,
                    target_url=url.target_url,
                    name=url.name,
                    clicks_count=url.clicks_count,
                    is_active=url.is_active,
                    created_at=url.created_at,
                    last_used=url.last_used,
                )
                for url in user_urls
            ],
        )
