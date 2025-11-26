__all__ = ("Urls",)

from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.infrastructures.db.models.base import Base

int_pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]


class Urls(Base):
    """A model class for storing shortened URLs."""

    __tablename__ = "urls"
    repr_cols_num = 5

    id: Mapped[int_pk] = mapped_column(doc="The primary key of the model.")

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        doc="Unique user identifier (UUID)",
        default=uuid4,
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        doc="The URL title/name.",
        nullable=True,
    )

    key: Mapped[str] = mapped_column(
        doc="The shortened URL key.",
        unique=True,
        index=True,
    )
    target_url: Mapped[str] = mapped_column(
        doc="The original URL.",
    )

    is_active: Mapped[bool] = mapped_column(
        doc="Whether the URL is active or not.",
        default=True,
    )
    clicks_count: Mapped[int] = mapped_column(
        doc="The number of times the URL has been clicked.",
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        doc="Creation date.",
        type_=DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_used: Mapped[datetime] = mapped_column(
        doc="Last used date.",
        type_=DateTime(timezone=True),
        nullable=True,
    )
