from dataclasses import dataclass

from shortener_app.application.interfaces.uow import UnitOfWorkProtocol
from tests.testkit.repository import FakeRepository


@dataclass
class FakeUnitOfWork(UnitOfWorkProtocol):
    repository: FakeRepository
    commit_calls: int = 0
    rollback_calls: int = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool | None:
        return None

    async def commit(self) -> None:
        self.commit_calls += 1

    async def rollback(self) -> None:
        self.rollback_calls += 1
