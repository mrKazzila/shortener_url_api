__all__ = (
    "EntityToDtoMapperProtocol",
    "DtoToEntityMapperProtocol",
    "EntityDtoMapperProtocol",
)

from typing import Protocol, TypeVar

E = TypeVar("E")  # Domain entity
D = TypeVar("D")  # Application DTO


class EntityToDtoMapperProtocol(Protocol[E, D]):
    """
    Application-layer mapper for converting Domain Entities into Application DTOs.

    One-way interface: prefer this when reverse mapping is not meaningful or not needed.
    """

    def to_dto(self, entity: E) -> D:
        """Map a domain entity into an application DTO."""
        ...


class DtoToEntityMapperProtocol(Protocol[D, E]):
    """
    Application-layer mapper for converting Application DTOs into Domain Entities.

    One-way interface: prefer this when DTO is an input boundary (e.g., create/update commands).
    """

    def to_entity(self, dto: D) -> E:
        """Map an application DTO into a domain entity."""
        ...


class EntityDtoMapperProtocol(
    EntityToDtoMapperProtocol[E, D],
    DtoToEntityMapperProtocol[D, E],
    Protocol[E, D],
):
    """
    Two-way mapper interface.

    Use only when both directions are truly required and semantically correct.
    """
