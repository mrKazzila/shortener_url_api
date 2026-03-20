__all__ = ("UpdateUrlUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

if TYPE_CHECKING:
    from shortener_app.application.dtos.urls.urls_requests import UpdateUrlDTO
    from shortener_app.application.interfaces import (
        UnitOfWorkProtocol,
    )
    from shortener_app.application.services.urls.url_reader import (
        UrlReaderService,
    )


logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateUrlUseCase:
    reader_service: "UrlReaderService"
    uow: "UnitOfWorkProtocol"

    async def execute(
        self,
        *,
        dto: "UpdateUrlDTO",
    ) -> bool:
        async with self.uow as uow:
            if entity := await self.reader_service.get_url_by_key(
                key=dto.key,
                repository=uow.repository,
            ):
                # FIXME update cache
                updated_entity = entity.update(
                    name=dto.name,
                    is_active=dto.is_active,
                )

                await uow.repository.update(entity=updated_entity)
                await uow.commit()

                return True

            return False
