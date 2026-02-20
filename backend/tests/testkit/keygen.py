from dataclasses import dataclass


@dataclass
class SequenceKeyGenerator:
    keys: list[str]
    calls: int = 0
    _idx: int = 0

    def __call__(self) -> str:
        self.calls += 1
        if not self.keys:
            raise RuntimeError("SequenceKeyGenerator.keys is empty")

        if self._idx >= len(self.keys):
            return self.keys[-1]

        key = self.keys[self._idx]
        self._idx += 1
        return key
