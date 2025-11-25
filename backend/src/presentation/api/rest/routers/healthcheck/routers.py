from fastapi import APIRouter, status

from src.presentation.api.schemas.info import SHealthStatus, StatusEnum

__all__ = ("router",)

router: APIRouter = APIRouter(
    prefix="/healthcheck",
    tags=["healthcheck"],
)


@router.get(
    path="/",
    name="Health status",
    status_code=status.HTTP_200_OK,
)
async def get_health() -> SHealthStatus:
    """Returns the health status of the application."""
    return SHealthStatus(status=StatusEnum.OK)
