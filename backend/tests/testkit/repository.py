from dataclasses import dataclass, field
from uuid import UUID

from shortener_app.application.interfaces.repository import RepositoryProtocol
from shortener_app.domain.entities.url import UrlEntity


@dataclass
class FakeRepository(RepositoryProtocol):
    get_result: UrlEntity | None = None
    get_calls: list[dict[str, str | int | UUID]] = field(default_factory=list)

    async def get(self, *, reference: dict[str, str | int | UUID]) -> UrlEntity | None:
        self.get_calls.append(reference)
        return self.get_result

    async def get_all(
        self,
        *,
        reference: dict[str, str | int | UUID],
        limit: int | None = None,
        last_id: int | UUID | None = None,
    ) -> list[UrlEntity]:
        raise NotImplementedError

    async def add(self, *, data: UrlEntity) -> None:
        raise NotImplementedError

    async def add_bulk(self, *, entities: list[UrlEntity]):
        raise NotImplementedError

    async def update(self, *, entity: UrlEntity) -> None:
        raise NotImplementedError

    async def delete(self, *, entity: UrlEntity) -> None:
        raise NotImplementedError

    async def apply_click_events(self, *, events: list[tuple[UUID, str]]) -> int:
        raise NotImplementedError
