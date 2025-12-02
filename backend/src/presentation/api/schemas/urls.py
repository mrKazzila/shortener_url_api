__all__ = ("SUrlResponse",)

from pydantic import BaseModel


class SUrlResponse(BaseModel):
    """Base URL schema."""

    key: str
    target_url: str
