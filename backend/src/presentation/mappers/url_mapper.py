__all__ = ("UrlPresentationMapper",)

from dataclasses import dataclass
from typing import final

from src.application.dtos.urls import CreatedUrlDTO
from src.presentation.api.schemas.urls import SUrlResponse


@final
@dataclass(frozen=True, slots=True)
class UrlPresentationMapper:
    @staticmethod
    def to_response(dto: CreatedUrlDTO) -> SUrlResponse:
        return SUrlResponse(
            key=dto.key,
            target_url=dto.target_url,
        )
