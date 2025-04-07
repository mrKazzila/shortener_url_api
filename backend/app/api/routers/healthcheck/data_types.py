import platform
from dataclasses import dataclass

from app.settings.config import settings


@dataclass(frozen=True, slots=True, kw_only=True)
class HealthStatus:
    status: str = "ok"


@dataclass(frozen=True, slots=True, kw_only=True)
class VersionInfo:
    app_version: str
    python_version: str
    system_info: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CpuInfo:
    usage_percent: float
    cores_physical: int
    cores_logical: int
    freq_current: float  # in MHz
    freq_max: float  # in MHz


@dataclass(frozen=True, slots=True, kw_only=True)
class MemoryInfo:
    usage_percent: float
    total: float  # in MB
    available: float  # in MB
    used: float  # in MB


@dataclass(frozen=True, slots=True, kw_only=True)
class DiskInfo:
    usage_percent: float
    total: float  # in GB
    free: float  # in GB
    used: float  # in GB


@dataclass(frozen=True, slots=True, kw_only=True)
class Metrics:
    cpu: CpuInfo
    memory: MemoryInfo
    disk: DiskInfo
    uptime: float  # in seconds


OK_STATUS = HealthStatus()
APP_VERSION = settings().APP_VERSION
VERSION_INFO = VersionInfo(
    app_version=APP_VERSION,
    python_version=platform.python_version(),
    system_info=f"{platform.system()} {platform.release()}",
)
