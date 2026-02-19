__all__ = ("PublishUrlJsonCodec",)

import json
from dataclasses import dataclass
from typing import Final
from uuid import UUID

from shortener_app.application.dtos.urls.urls_events import PublishUrlDTO
from shortener_app.application.interfaces.dto_codec import DtoCodecProtocol


@dataclass(frozen=True, slots=True)
class PublishUrlJsonCodec(DtoCodecProtocol[PublishUrlDTO, bytes]):
    """
    Infrastructure codec: PublishUrlDTO <-> JSON bytes.

    Intended usage:
    - broker message payloads
    - any wire format where the external representation is bytes

    Design notes:
    - The JSON schema is explicit to avoid surprising changes from dataclasses.asdict().
    - UUID values are encoded as strings for portability.
    """

    _encoding: Final[str] = "utf-8"

    def encode(self, dto: PublishUrlDTO) -> bytes:
        """Serialize PublishUrlDTO into UTF-8 JSON bytes."""
        payload = {
            "key": dto.key,
            "target_url": dto.target_url,
            "user_id": str(dto.user_id),
        }
        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode(self._encoding)

    def decode(self, raw: bytes) -> PublishUrlDTO:
        """Deserialize UTF-8 JSON bytes into PublishUrlDTO."""
        data = json.loads(raw.decode(self._encoding))
        return PublishUrlDTO(
            key=data["key"],
            target_url=data["target_url"],
            user_id=UUID(data["user_id"]),
        )
