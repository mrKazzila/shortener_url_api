from typing import Annotated

from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

int_pk = Annotated[int, mapped_column(primary_key=True)]


class Urls(Base):
    """A model class for storing shortened URLs."""

    __tablename__ = "urls"
    repr_cols_num = 4

    id: Mapped[int_pk] = mapped_column(doc="The primary key of the model.")
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
