from pydantic import BaseModel

__all__ = ("SUrlResponse",)


class SUrlResponse(BaseModel):
    """Base URL schema."""

    key: str
    target_url: str
