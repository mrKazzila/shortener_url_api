__all__ = ("UserPresentationMapper",)

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import final

from google.protobuf.timestamp_pb2 import Timestamp

from src.domain.entities.url import UrlEntity
from src.generated.user_urls.v1 import user_urls_pb2


@final
@dataclass(frozen=True, slots=True)
class UserPresentationMapper:
    @staticmethod
    def to_proto_get_user_urls_response(
        user_urls: list["UrlEntity"],
    ) -> user_urls_pb2.GetUserUrlsResponse:
        items = []

        for url in user_urls:
            item = user_urls_pb2.UserUrl(
                key=url.key,
                target_url=url.target_url,
                name=url.name,
                clicks_count=url.clicks_count,
                is_active=url.is_active,
                created_at=UserPresentationMapper._dt_to_timestamp(
                    url.created_at,
                ),
                last_used=UserPresentationMapper._dt_to_timestamp(
                    url.last_used,
                ),
            )

            items.append(item)

        return user_urls_pb2.GetUserUrlsResponse(
            items=items,
            count=len(user_urls),
        )

    @staticmethod
    def _dt_to_timestamp(dt: datetime):
        ts = Timestamp()

        ts.FromDatetime(
            dt.replace(tzinfo=UTC)
            if dt.tzinfo is None
            else dt.astimezone(UTC),
        )
        return ts
