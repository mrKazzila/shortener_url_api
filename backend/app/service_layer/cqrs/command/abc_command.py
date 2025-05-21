from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.service_layer.unit_of_work.uow import UnitOfWork


__all__ = ("ABCCommandService",)


class ABCCommandService:
    __slots__ = ("uow",)

    def __init__(self, *, uow: "UnitOfWork") -> None:
        self.uow = uow
