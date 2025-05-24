from app.dto.urls import ClickedUrlDTO
from app.service_layer.cqrs.command.abc_command import ABCCommandService

__all__ = ("UrlCommandService",)


class UrlCommandService(ABCCommandService):
    async def create_short_url(self, *, url_data: dict) -> None:
        async with self.uow as uow:
            await uow.urls_repo.add(data=url_data)
            await uow.commit()

    async def update_click_data(self, *, key: str) -> ClickedUrlDTO | None:
        async with self.uow as uow:
            result = await uow.urls_repo.increment_clicks_and_return(key=key)
            if not result:
                return None
            return ClickedUrlDTO(
                key=str(result.key),
                target_url=str(result.target_url),
                clicks_count=int(result.clicks_count),
            )
