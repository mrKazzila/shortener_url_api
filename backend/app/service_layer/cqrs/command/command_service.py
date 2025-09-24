from app.service_layer.cqrs.command.abc_command import ABCCommandService

__all__ = ("UrlCommandService",)


class UrlCommandService(ABCCommandService):
    async def create_short_url(self, *, url_data: dict) -> None:
        async with self.uow as uow:
            await uow.urls_repo.add(data=url_data)
            await uow.commit()

    async def update_click_data(self, *, url_id: int) -> None:
        async with self.uow as uow:
            async with uow:
                await uow.urls_repo.increment_clicks(url_id=url_id)
                await uow.commit()
