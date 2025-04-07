import time

import psutil
from fastapi import APIRouter, status

from app.api.routers.healthcheck.data_types import (
    OK_STATUS,
    VERSION_INFO,
    CpuInfo,
    DiskInfo,
    HealthStatus,
    MemoryInfo,
    Metrics,
    VersionInfo,
)

router = APIRouter(
    prefix="/service_info",
    tags=["service_info"],
)

START_TIME = time.time()

__all__ = ("router",)


@router.get(
    path="/health",
    name="Health status",
    status_code=status.HTTP_200_OK,
)
async def get_health() -> HealthStatus:
    """Returns the health status of the application."""
    return OK_STATUS


@router.get(
    path="/version",
    name="Version info",
    status_code=status.HTTP_200_OK,
)
async def get_version() -> VersionInfo:
    """Returns version information about the service."""
    return VERSION_INFO


def bytes_to_mb(bytes_val: float) -> float:
    return round(bytes_val / (1024 * 1024), 2)


def bytes_to_gb(bytes_val: float) -> float:
    return round(bytes_val / (1024 * 1024 * 1024), 2)


@router.get(
    path="/metrics",
    name="Service metrics",
    status_code=status.HTTP_200_OK,
)
async def get_metrics() -> Metrics:
    """Returns detailed technical metrics of the service."""
    cpu_usage = psutil.cpu_percent()
    cpu_freq = psutil.cpu_freq()
    cpu_info = CpuInfo(
        usage_percent=cpu_usage,
        cores_physical=psutil.cpu_count(logical=False),
        cores_logical=psutil.cpu_count(logical=True),
        freq_current=cpu_freq.current if cpu_freq else 0,
        freq_max=cpu_freq.max if cpu_freq else 0,
    )

    mem = psutil.virtual_memory()
    memory_info = MemoryInfo(
        usage_percent=mem.percent,
        total=bytes_to_mb(mem.total),
        available=bytes_to_mb(mem.available),
        used=bytes_to_mb(mem.used),
    )

    disk = psutil.disk_usage("/")
    disk_info = DiskInfo(
        usage_percent=disk.percent,
        total=bytes_to_gb(disk.total),
        free=bytes_to_gb(disk.free),
        used=bytes_to_gb(disk.used),
    )

    uptime = time.time() - START_TIME

    return Metrics(
        cpu=cpu_info,
        memory=memory_info,
        disk=disk_info,
        uptime=uptime,
    )
