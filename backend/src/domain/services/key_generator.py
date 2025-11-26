__all__ = ("RandomKeyGenerator",)

from dataclasses import dataclass
from random import choices
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

    def __call__(self) -> str:
        return "".join(
            choices(
                self.chars,  # type: ignore
                k=self.length,
            ),
        )
