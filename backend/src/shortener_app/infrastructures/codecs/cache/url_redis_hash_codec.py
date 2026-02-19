__all__ = ("UrlCacheRedisHashCodec",)

from dataclasses import dataclass
from uuid import UUID

from shortener_app.application.dtos.urls.urls_cache import UrlCacheRecordDTO
from shortener_app.application.interfaces.dto_codec import DtoCodecProtocol


@dataclass(frozen=True, slots=True)
class UrlCacheRedisHashCodec(
    DtoCodecProtocol[UrlCacheRecordDTO, dict[str, str]],
):
    """
    Infrastructure codec: UrlCacheRecordDTO <-> Redis HASH representation.

    Redis HASH stores string/bytes values. This codec normalizes types:
    - UUID -> str
    - bool -> "1"/"0"
    - None -> "" (empty string)
    """

    def encode(self, dto: UrlCacheRecordDTO) -> dict[str, str]:
        return {
            "key": dto.key,
            "target_url": dto.target_url,
            "user_id": str(dto.user_id),
            "name": dto.name or "",
            "is_active": "1" if dto.is_active else "0",
        }

    def decode(self, raw: dict[str, str]) -> UrlCacheRecordDTO:
        return UrlCacheRecordDTO(
            key=raw["key"],
            target_url=raw["target_url"],
            user_id=UUID(raw["user_id"]),
            name=raw.get("name") or None,
            is_active=raw.get("is_active", "0") == "1",
        )
