from app.service_layer.cqrs.command.abc_command import ABCCommandService

__all__ = ("UrlCommandService",)


class UrlCommandService(ABCCommandService):
    async def create_short_url(self, *, url_data: dict) -> None:
        async with self.uow as uow:
            await uow.urls_repo.add(data=url_data)
            await uow.commit()

    async def update_click_data(
        self,
        *,
        model_id: int,
        url_data: dict,
    ) -> None:
        async with self.uow as uow:
            await uow.urls_repo.update(
                model_id=model_id,
                **url_data,
            )
            await uow.commit()
