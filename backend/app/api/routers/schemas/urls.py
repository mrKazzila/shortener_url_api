from pydantic import BaseModel

__all__ = (
    "SUrlBase",
    "SUrl",
    "SUrlInfo",
    "SReturnUrl",
)


class SUrlBase(BaseModel):
    """Base URL schema."""

    target_url: str


class SReturnUrl(SUrlBase):
    key: str


class SUrl(SUrlBase):
    """URL schema."""

    id: int


class SUrlInfo(SUrl):
    """SUrlInfo schema."""

    is_active: bool
    clicks_count: int
