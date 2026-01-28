__all__ = ("UrlPresentationMapper",)

from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, slots=True)
class UrlPresentationMapper:
    ...
