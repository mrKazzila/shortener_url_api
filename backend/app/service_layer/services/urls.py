import logging
from random import choices
from string import ascii_letters, digits
from typing import TYPE_CHECKING

from validators import url as url_validator

from app.dto.urls import (
    CreatedUrlDTO,
    DBUrlDTO,
    UrlDTO,
    UrlInfoDTO,
)
from app.exceptions.urls import InvalidUrlException, UrlNotFoundException
from app.settings.config import settings

if TYPE_CHECKING:
    from uuid import UUID

    from redis.asyncio import Redis

    from app.service_layer.cqrs import QueryService, UrlCommandService


__all__ = ("UrlsServices",)

logger = logging.getLogger(__name__)


class UrlsServices:
    CHARS = f"{ascii_letters}{digits}"
    LENGTH = settings.KEY_LENGTH

    __slots__ = ("redis", "query_service", "command_service")

    def __init__(
        self,
        *,
        redis: "Redis",
        query_service: "QueryService",
        command_service: "UrlCommandService",
    ) -> None:
        self.redis = redis
        self.query_service = query_service
        self.command_service = command_service

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    async def create_url(
        self,
        *,
        url_data: UrlDTO,
    ) -> CreatedUrlDTO:
        """Create a new URL in the database."""
        if not url_validator(url_data.target_url):
            raise InvalidUrlException()

        key = self._generate_random_key()
        is_set_in_cache = await self._try_set_redis_key(key=key)

        if not is_set_in_cache:
            key = await self._create_unique_random_key()

        await self.command_service.create_short_url(
            url_data={
                "user_id": url_data.user_id,
                "key": key,
                "target_url": url_data.target_url,
            },
        )

        return CreatedUrlDTO(
            user_id=url_data.user_id,
            key=key,
            target_url=url_data.target_url,
        )

    async def update_redirect_counter(self, *, key: str) -> str:
        if not (url := await self.query_service.get_url_by_key(url_key=key)):
            raise UrlNotFoundException(url_key=key)

        await self.command_service.update_click_data(url_id=url.id)
        return url.target_url

    async def get_user_urls(
        self,
        *,
        user_id: "UUID",
        pagination_data: dict[str, int | None],
    ) -> list[DBUrlDTO | None]:
        return await self.query_service.get_all_user_urls(
            user_id=user_id,
            pagination_data=pagination_data,
        )

    async def _create_unique_random_key(self) -> str:
        """Creates a unique random key."""
        while True:
            key = self._generate_random_key()
            is_key_exist = await self._get_active_long_url_by_key(key=key)

            if not is_key_exist:
                await self._try_set_redis_key(key=key)
                return key

    async def _get_active_long_url_by_key(
        self,
        *,
        key: str,
    ) -> UrlInfoDTO | None:
        """Get a URL from the database by its key."""
        if not (
            long_url := await self.query_service.get_url_by_key(url_key=key)
        ):
            return None

        return UrlInfoDTO(
            id=long_url.id,
            target_url=long_url.target_url,
            is_active=long_url.is_active,
            clicks_count=long_url.clicks_count,
        )

    async def _try_set_redis_key(self, key: str) -> bool:
        return await self.redis.hsetnx("urls_hash", key, "1")

    def _generate_random_key(self) -> str:
        """Generate a random key of the given length."""
        return "".join(choices(self.CHARS, k=self.LENGTH))  # type: ignore
