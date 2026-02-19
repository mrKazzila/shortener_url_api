__all__ = ("UserPresentationMapper",)

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import final

from google.protobuf.timestamp_pb2 import Timestamp  # noqa
from shortener_app.generated.user_urls.v1 import user_urls_pb2

from shortener_app.application.dtos.users.user_responses import (
    GetUserUrlsResultDTO,
)


@final
@dataclass(frozen=True, slots=True)
class UserPresentationMapper:
    """
    Presentation-layer mapper for the UserUrls gRPC API.

    Converts Application output DTOs into protobuf responses and handles protobuf-specific types.
    """

    def to_proto_get_user_urls_response(
        self,
        result: GetUserUrlsResultDTO,
    ) -> user_urls_pb2.GetUserUrlsResponse:
        items: list[user_urls_pb2.UserUrl] = []

        for dto in result.items:
            item = user_urls_pb2.UserUrl(
                key=dto.key,
                target_url=dto.target_url,
                name=dto.name or "",
                clicks_count=dto.clicks_count,
                is_active=dto.is_active,
            )

            # timestamps (safer than passing possibly-None directly)
            item.created_at.CopyFrom(self._dt_to_timestamp(dto.created_at))
            if dto.last_used is not None:
                item.last_used.CopyFrom(self._dt_to_timestamp(dto.last_used))

            items.append(item)

        return user_urls_pb2.GetUserUrlsResponse(
            items=items,
            count=result.count,
        )

    @staticmethod
    def _dt_to_timestamp(dt: datetime) -> Timestamp:
        """Convert a Python datetime into google.protobuf.Timestamp (UTC)."""
        ts = Timestamp()
        ts.FromDatetime(
            dt.replace(tzinfo=UTC)
            if dt.tzinfo is None
            else dt.astimezone(UTC),
        )
        return ts
