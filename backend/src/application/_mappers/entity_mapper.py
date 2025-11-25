from abc import abstractmethod
from typing import Protocol

from src.application.dtos.urls import CreatedUrlDTO, DBUrlDTO
from src.domain.entities.url import UrlEntity


class DtoEntityMapperProtocol(Protocol):
    """Protocol for Application layer mapper (Domain Entity <-> Application DTO)."""

    @abstractmethod
    def to_dto(self, entity: UrlEntity) -> DBUrlDTO:
        """Converts a Domain Entity to an Application DTO."""
        ...

    @abstractmethod
    def to_entity(self, dto: DBUrlDTO) -> UrlEntity:
        """Converts an Application DTO to a Domain Entity."""
        ...

    @abstractmethod
    def to_created_dto(
        self,
        entity: UrlEntity,
    ) -> CreatedUrlDTO:
        """Converts a Domain Entity to an ArtifactAdmissionNotificationDTO."""
        ...
