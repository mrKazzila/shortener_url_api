from dataclasses import dataclass

__all__ = (
    "CpuInfoDTO",
    "DiskInfoDTO",
    "HealthStatusDTO",
    "MemoryInfoDTO",
    "MetricsDTO",
    "VersionInfoDTO",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class HealthStatusDTO:
    status: str = "ok"


@dataclass(frozen=True, slots=True, kw_only=True)
class VersionInfoDTO:
    app_version: str
    python_version: str
    system_info: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CpuInfoDTO:
    usage_percent: float
    cores_physical: int
    cores_logical: int
    freq_current: float  # in MHz
    freq_max: float  # in MHz


@dataclass(frozen=True, slots=True, kw_only=True)
class MemoryInfoDTO:
    usage_percent: float
    total: float  # in MB
    available: float  # in MB
    used: float  # in MB


@dataclass(frozen=True, slots=True, kw_only=True)
class DiskInfoDTO:
    usage_percent: float
    total: float  # in GB
    free: float  # in GB
    used: float  # in GB


@dataclass(frozen=True, slots=True, kw_only=True)
class MetricsDTO:
    cpu: CpuInfoDTO
    memory: MemoryInfoDTO
    disk: DiskInfoDTO
    uptime: float  # in seconds
