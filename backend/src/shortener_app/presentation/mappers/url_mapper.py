__all__ = ("UrlPresentationMapper",)

from dataclasses import dataclass
from typing import final
from uuid import UUID

from shortener_app.generated.shortener.v1 import shortener_pb2

from shortener_app.application.dtos.urls.urls_requests import (
    CreateUrlDTO,
    DeleteUrlDTO,
    UpdateUrlDTO,
)
from shortener_app.application.dtos.urls.urls_responses import CreatedUrlDTO


@final
@dataclass(frozen=True, slots=True)
class UrlPresentationMapper:
    """
    Presentation-layer mapper for the Shortener gRPC API.

    Responsibilities:
    - Convert protobuf requests into Application DTOs for use-cases.
    - Convert use-case results (DTOs / primitives) into protobuf responses.
    - Keep gRPC/service layer thin and boring.

    Notes:
    - This mapper must not depend on ORM models or Redis/broker formats.
    """

    # -------- Requests -> Application DTOs --------

    def to_create_url_dto(
        self,
        request: shortener_pb2.CreateShortUrlRequest,
        *,
        user_id: UUID,
    ) -> CreateUrlDTO:
        """Convert CreateShortUrlRequest into CreateUrlDTO."""
        return CreateUrlDTO(
            target_url=request.target_url,
            user_id=user_id,
        )

    def to_update_url_dto(
        self,
        request: shortener_pb2.UpdateUrlRequest,
    ) -> UpdateUrlDTO:
        """Convert UpdateUrlRequest into UpdateUrlDTO."""
        return UpdateUrlDTO(
            key=request.key,
            name=request.name,
            is_active=request.is_active,
        )

    def to_delete_url_dto(
        self,
        request: shortener_pb2.DeleteUrlRequest,
    ) -> DeleteUrlDTO:
        """Convert DeleteUrlRequest into DeleteUrlDTO."""
        return DeleteUrlDTO(key=request.key)

    # -------- Use-case results -> Responses --------

    def to_create_short_url_response(
        self,
        result: CreatedUrlDTO,
    ) -> shortener_pb2.CreateShortUrlResponse:
        """Convert CreatedUrlDTO into CreateShortUrlResponse."""
        return shortener_pb2.CreateShortUrlResponse(
            key=result.key,
            target_url=result.target_url,
        )

    def to_resolve_key_response(
        self,
        target_url: str,
    ) -> shortener_pb2.ResolveKeyResponse:
        """Convert a resolved target URL into ResolveKeyResponse."""
        return shortener_pb2.ResolveKeyResponse(target_url=target_url)

    def to_update_url_response(
        self,
        ok: bool,
    ) -> shortener_pb2.UpdateUrlResponse:
        return shortener_pb2.UpdateUrlResponse(
            ok="Ok" if ok else "Error",
        )

    def to_delete_url_response(
        self,
        ok: bool,
    ) -> shortener_pb2.DeleteUrlResponse:
        return shortener_pb2.DeleteUrlResponse(
            ok="Ok" if ok else "Error",
        )
