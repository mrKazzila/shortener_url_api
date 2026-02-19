__all__ = ("DtoCodecProtocol",)

from typing import Protocol, TypeVar

D = TypeVar("D")  # Application DTO
R = TypeVar("R")  # External representation: bytes | dict[str, str] | ...


class DtoCodecProtocol(Protocol[D, R]):
    """
    DTO codec interface.

    Encodes/decodes an Application-layer DTO to/from an external representation
    used by infrastructure concerns such as brokers, caches, or wire formats.

    Notes:
    - This interface is intentionally DTO-centric: it must not depend on Domain entities.
    - Implementations typically live in the Infrastructure layer.
    """

    def encode(self, dto: D) -> R:
        """Convert a DTO into an external representation."""
        ...

    def decode(self, raw: R) -> D:
        """Convert an external representation back into a DTO."""
        ...
