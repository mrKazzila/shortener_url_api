__all__ = (
    "StatusEnum",
    "SHealthStatus",
)


from enum import StrEnum

from pydantic import BaseModel


class StatusEnum(StrEnum):
    OK = "ok"


class SHealthStatus(BaseModel):
    status: StatusEnum = StatusEnum.OK
