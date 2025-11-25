from abc import abstractmethod
from typing import Protocol

from src.domain.entities.url import UrlEntity


class SerializationMapperProtocol(Protocol):
    """
    Protocol for serialization/deserialization of Application DTOs.

    This interface allows the Application layer to serialize DTOs
    without depending on Infrastructure implementations.
    """

    @abstractmethod
    def to_dict(self, dto: UrlEntity) -> dict:
        """
        Converts an Application DTO to a dictionary for serialization.

        Args:
            dto: The UrlEntity to convert.

        Returns:
            A dictionary representation of the DTO.
        """
        ...

    @abstractmethod
    def from_dict(self, data: dict) -> UrlEntity:
        """
        Converts a dictionary from deserialization back to an Application DTO.

        Args:
            data: The dictionary to convert.

        Returns:
            An UrlEntity object.
        """
        ...