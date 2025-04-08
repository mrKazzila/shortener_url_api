import logging
from platform import (
    python_version as platform_python_version,
    release as platform_release,
    system as platform_system,
)
from time import time

import psutil

from app.dto.info import (
    CpuInfoDTO,
    DiskInfoDTO,
    HealthStatusDTO,
    MemoryInfoDTO,
    MetricsDTO,
    VersionInfoDTO,
)
from app.settings.config import settings

__all__ = ("InfoServices",)

logger = logging.getLogger(__name__)

START_TIME = time()


class InfoServices:
    @classmethod
    def get_health(cls):
        return HealthStatusDTO()

    @classmethod
    def get_version(cls) -> VersionInfoDTO:
        return VersionInfoDTO(
            app_version=settings().APP_VERSION,
            python_version=platform_python_version(),
            system_info=f"{platform_system()} {platform_release()}",
        )

    @classmethod
    def get_metrics(cls) -> MetricsDTO:
        """Returns detailed technical metrics of the service."""
        cpu_usage = psutil.cpu_percent()
        cpu_freq = psutil.cpu_freq()
        cpu_info = CpuInfoDTO(
            usage_percent=cpu_usage,
            cores_physical=psutil.cpu_count(logical=False),
            cores_logical=psutil.cpu_count(logical=True),
            freq_current=cpu_freq.current if cpu_freq else 0,
            freq_max=cpu_freq.max if cpu_freq else 0,
        )

        mem = psutil.virtual_memory()
        memory_info = MemoryInfoDTO(
            usage_percent=mem.percent,
            total=cls._bytes_to_mb(mem.total),
            available=cls._bytes_to_mb(mem.available),
            used=cls._bytes_to_mb(mem.used),
        )

        disk = psutil.disk_usage("/")
        disk_info = DiskInfoDTO(
            usage_percent=disk.percent,
            total=cls._bytes_to_gb(disk.total),
            free=cls._bytes_to_gb(disk.free),
            used=cls._bytes_to_gb(disk.used),
        )

        return MetricsDTO(
            cpu=cpu_info,
            memory=memory_info,
            disk=disk_info,
            uptime=time() - START_TIME,
        )

    @staticmethod
    def _bytes_to_mb(bytes_val: float) -> float:
        return round(bytes_val / (1024 * 1024), 2)

    @staticmethod
    def _bytes_to_gb(bytes_val: float) -> float:
        return round(bytes_val / (1024 * 1024 * 1024), 2)
