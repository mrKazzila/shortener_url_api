from fastapi import Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    limit: int = Query(10, ge=1, le=100)
    last_id: int | None = None


def pagination_params(
    limit: int = 10,
    last_id: int | None = None,
) -> PaginationParams:
    return PaginationParams(
        limit=limit,
        last_id=last_id,
    )
