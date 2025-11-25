from typing import final

from src.application.dtos.urls import CreatedUrlDTO
from src.presentation.api.rest.schemas.urls import SUrlResponse

__all__ = ("UrlPresentationMapper",)


@final
class UrlPresentationMapper:
    @staticmethod
    def to_response(dto: CreatedUrlDTO) -> SUrlResponse:
        return SUrlResponse(
            key=dto.key,
            target_url=dto.target_url,
        )
