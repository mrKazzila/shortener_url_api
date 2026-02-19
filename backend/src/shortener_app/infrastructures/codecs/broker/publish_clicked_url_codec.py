__all__ = ("UrlClickedJsonCodec",)

import json
from dataclasses import dataclass
from typing import Final
from uuid import UUID

from shortener_app.application.dtos.urls.urls_events import UrlClickedEventDTO
from shortener_app.application.interfaces.dto_codec import DtoCodecProtocol


@dataclass(frozen=True, slots=True)
class UrlClickedJsonCodec(DtoCodecProtocol[UrlClickedEventDTO, bytes]):
    _encoding: Final[str] = "utf-8"

    def encode(self, dto: UrlClickedEventDTO) -> bytes:
        payload = {
            "key": dto.key,
            "event_id": str(dto.event_id),
        }
        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode(self._encoding)

    def decode(self, raw: bytes) -> UrlClickedEventDTO:
        data = json.loads(raw.decode(self._encoding))
        return UrlClickedEventDTO(
            key=data["key"],
            event_id=UUID(data["event_id"]),
        )
