import logging

from validators import url as url_validator

from app.api.routers.urls.utils import generate_random_key
from app.dto.urls import CreatedUrlDTO, UrlInfoDTO
from app.service_layer.services.exceptions import (
    InvalidUrlException,
    UrlNotFoundException,
)
from app.service_layer.unit_of_work import UnitOfWork

__all__ = ("UrlsServices",)

logger = logging.getLogger(__name__)


class UrlsServices:
    __slots__ = ("uow",)

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    async def create_url(
        self,
        *,
        target_url: str,
    ) -> CreatedUrlDTO:
        """Create a new URL in the database."""
        if not url_validator(target_url):
            raise InvalidUrlException()

        async with self.uow as transaction:
            key_ = await self._create_unique_random_key(
                transaction=transaction,
            )
            result = await transaction.urls_repo.add(
                target_url=str(target_url),
                key=key_,
            )
            await transaction.commit()

        return CreatedUrlDTO(
            key=result.key,
            target_url=result.target_url,
        )

    async def update_redirect_counter_for_url(
        self,
        *,
        key: str,
    ) -> str:
        async with self.uow as transaction:
            if db_url := await self._get_active_long_url_by_key(
                key=key,
                transaction=transaction,
            ):
                await self._update_db_clicks(
                    url=db_url,
                    transaction=transaction,
                )
                return str(db_url.target_url)

        raise UrlNotFoundException(url_key=key)

    @staticmethod
    async def _get_active_long_url_by_key(
        *,
        key: str,
        transaction: UnitOfWork,
    ) -> UrlInfoDTO | None:
        """Get a URL from the database by its key."""
        _reference = {"key": key}

        if long_url := await transaction.urls_repo.get(reference=_reference):
            return UrlInfoDTO(
                id=long_url.id,
                target_url=long_url.target_url,
                is_active=long_url.is_active,
                clicks_count=long_url.clicks_count,
            )

        return None

    async def _create_unique_random_key(
        self,
        *,
        transaction: UnitOfWork,
    ) -> str:
        """Creates a unique random key."""
        key = generate_random_key()

        while await self._get_active_long_url_by_key(
            key=key,
            transaction=transaction,
        ):
            key = generate_random_key()

        return key

    @staticmethod
    async def _update_db_clicks(
        *,
        url: UrlInfoDTO,
        transaction: UnitOfWork,
    ) -> None:
        """Update the clicks count for a URL in the database."""
        await transaction.urls_repo.update(
            model_id=url.id,
            clicks_count=url.clicks_count + 1,
        )
        await transaction.commit()
