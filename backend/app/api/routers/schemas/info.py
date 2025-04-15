from enum import StrEnum

from pydantic import BaseModel

__all__ = (
    "SHealthStatus",
    "SVersionInfo",
    "SMetrics",
    "SCpuInfo",
    "SMemoryInfo",
    "SDiskInfo",
)


class StatusEnum(StrEnum):
    OK = "ok"


class SHealthStatus(BaseModel):
    status: StatusEnum = StatusEnum.OK


class SVersionInfo(BaseModel):
    app_version: str
    python_version: str
    system_info: str


class SCpuInfo(BaseModel):
    usage_percent: float
    cores_physical: int
    cores_logical: int
    freq_current_mhz: float
    freq_max_mhz: float


class SMemoryInfo(BaseModel):
    usage_percent: float
    total_mb: float
    available_mb: float
    used_mb: float


class SDiskInfo(BaseModel):
    usage_percent: float
    total_gb: float
    free_gb: float
    used_gb: float


class SMetrics(BaseModel):
    cpu: SCpuInfo
    memory: SMemoryInfo
    disk: SDiskInfo
    uptime_sec: float
