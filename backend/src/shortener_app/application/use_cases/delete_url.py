__all__ = ("DeleteUrlUseCase",)

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

import structlog

from shortener_app.application.dtos.urls.urls_requests import DeleteUrlDTO

if TYPE_CHECKING:
    from shortener_app.application.interfaces import (
        CacheProtocol,
        UnitOfWorkProtocol,
    )
    from shortener_app.application.services.urls.url_reader import (
        UrlReaderService,
    )

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteUrlUseCase:
    reader_service: "UrlReaderService"
    cache: "CacheProtocol"
    uow: "UnitOfWorkProtocol"

    async def execute(
        self,
        *,
        dto: DeleteUrlDTO,
    ) -> bool:
        async with self.uow as uow:
            if entity := await self.reader_service.get_url_by_key(
                key=dto.key,
                repository=uow.url_repository,
            ):
                await self.cache.delete(key=f"short:{entity.key}")

                await uow.url_repository.delete(entity=entity)
                await uow.commit()

                return True

            return False
