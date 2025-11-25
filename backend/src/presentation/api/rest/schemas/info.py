from enum import StrEnum

from pydantic import BaseModel

__all__ = (
    "StatusEnum",
    "SHealthStatus",
)


class StatusEnum(StrEnum):
    OK = "ok"


class SHealthStatus(BaseModel):
    status: StatusEnum = StatusEnum.OK
