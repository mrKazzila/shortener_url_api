__all__ = ("RandomKeyGenerator",)

from dataclasses import dataclass, field
from random import SystemRandom
from string import ascii_letters, digits
from typing import final


@final
@dataclass(frozen=True, slots=True)
class RandomKeyGenerator:
    """
    Generate a random key of the given length.
    """

    length: int = 5
    chars: str = f"{ascii_letters}{digits}"
    random: SystemRandom = field(default_factory=SystemRandom)

    def __post_init__(self) -> None:
        if self.length < 0:
            raise ValueError("length must be >= 0")
        if not self.chars and self.length > 0:
            raise ValueError("chars must be non-empty when length > 0")

    def __call__(self) -> str:
        return "".join(
            self.random.choices(population=self.chars, k=self.length),
        )
