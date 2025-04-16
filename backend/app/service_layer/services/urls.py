import logging
from random import choice
from string import ascii_letters, digits
from typing import TYPE_CHECKING

from validators import url as url_validator

from app.dto.urls import CreatedUrlDTO, UrlInfoDTO
from app.exceptions.urls import (
    InvalidUrlException,
    UrlNotFoundException,
)
from app.settings.config import settings

if TYPE_CHECKING:
    from redis.asyncio import Redis

    from app.service_layer.unit_of_work import UnitOfWork


__all__ = ("UrlsServices",)

logger = logging.getLogger(__name__)


class UrlsServices:
    CHARS = f"{ascii_letters}{digits}"
    LENGTH = settings.KEY_LENGTH

    __slots__ = ("redis", "uow")

    def __init__(self, redis: "Redis", uow: "UnitOfWork") -> None:
        self.redis = redis
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

        key = self._generate_random_key()

        if await self._try_set_redis_key(
            key=key,
            target_url=target_url,
        ):
            async with self.uow as transaction:
                result = await transaction.urls_repo.add(
                    target_url=str(target_url),
                    key=key,
                )
                await transaction.commit()

                return CreatedUrlDTO(
                    key=result.key,
                    target_url=result.target_url,
                )

        async with self.uow as transaction:
            key = await self._create_unique_random_key(
                transaction=transaction,
                long_url=target_url,
            )
            result = await transaction.urls_repo.add(
                target_url=str(target_url),
                key=key,
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

    async def _create_unique_random_key(
        self,
        *,
        transaction: "UnitOfWork",
        long_url: str,
    ) -> str:
        """Creates a unique random key."""
        while True:
            key = self._generate_random_key()

            if not await self._get_active_long_url_by_key(
                key=key,
                transaction=transaction,
            ):
                await self._try_set_redis_key(key=key, target_url=long_url)
                return key

    @staticmethod
    async def _get_active_long_url_by_key(
        *,
        key: str,
        transaction: "UnitOfWork",
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

    @staticmethod
    async def _update_db_clicks(
        *,
        url: UrlInfoDTO,
        transaction: "UnitOfWork",
    ) -> None:
        """Update the clicks count for a URL in the database."""
        await transaction.urls_repo.update(
            model_id=url.id,
            clicks_count=url.clicks_count + 1,
        )
        await transaction.commit()

    async def _try_set_redis_key(self, key: str, target_url: str) -> bool:
        return await self.redis.set(f"url:{key}", target_url, nx=True)

    def _generate_random_key(self) -> str:
        """Generate a random key of the given length."""
        return "".join(choice(self.CHARS) for _ in range(self.LENGTH))
