from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.api.routers.schemas.info import (
    SCpuInfo,
    SDiskInfo,
    SHealthStatus,
    SMemoryInfo,
    SMetrics,
    SVersionInfo,
)
from app.service_layer.services import InfoServices

__all__ = ("router",)

router = APIRouter(
    prefix="/service_info",
    tags=["service_info"],
    route_class=DishkaRoute,
)


@router.get(
    path="/health",
    name="Health status",
    status_code=status.HTTP_200_OK,
)
async def get_health(
    info_service: FromDishka[InfoServices],
) -> SHealthStatus:
    """Returns the health status of the application."""
    health = info_service.get_health()
    return SHealthStatus(status=health.status)


@router.get(
    path="/version",
    name="Version info",
    status_code=status.HTTP_200_OK,
)
async def get_version(
    info_service: FromDishka[InfoServices],
) -> SVersionInfo:
    """Returns version information about the service."""
    version = info_service.get_version()
    return SVersionInfo(
        app_version=version.app_version,
        python_version=version.python_version,
        system_info=version.system_info,
    )


@router.get(
    path="/metrics",
    name="Service metrics",
    status_code=status.HTTP_200_OK,
)
async def get_metrics(
    info_service: FromDishka[InfoServices],
) -> SMetrics:
    """Returns detailed technical metrics of the service."""
    metrics = info_service.get_metrics()
    return SMetrics(
        cpu=SCpuInfo(
            usage_percent=metrics.cpu.usage_percent,
            cores_physical=metrics.cpu.cores_physical,
            cores_logical=metrics.cpu.cores_logical,
            freq_current_mhz=metrics.cpu.freq_current,
            freq_max_mhz=metrics.cpu.freq_max,
        ),
        memory=SMemoryInfo(
            usage_percent=metrics.memory.usage_percent,
            total_mb=metrics.memory.total,
            available_mb=metrics.memory.available,
            used_mb=metrics.memory.used,
        ),
        disk=SDiskInfo(
            usage_percent=metrics.disk.usage_percent,
            total_gb=metrics.disk.total,
            free_gb=metrics.disk.free,
            used_gb=metrics.disk.used,
        ),
        uptime_sec=metrics.uptime,
    )
