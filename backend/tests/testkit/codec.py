from dataclasses import dataclass, field
from typing import Any


@dataclass
class SpyDtoCodec:
    return_value: Any = field(default_factory=dict)
    decode_value: Any = None

    encode_calls: list[Any] = field(default_factory=list)
    decode_calls: list[Any] = field(default_factory=list)

    def encode(self, dto: Any) -> Any:
        self.encode_calls.append(dto)
        if isinstance(self.return_value, dict):
            return dict(self.return_value)
        return self.return_value

    def decode(self, raw: Any) -> Any:
        self.decode_calls.append(raw)
        return self.decode_value
