__all__ = ("ClickInbox",)

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructures.db.models.base import Base


class ClickInbox(Base):
    __tablename__ = "click_inbox"

    event_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        doc="Event ID.",
        primary_key=True,
        default=uuid4,
    )
    url_key: Mapped[str] = mapped_column(
        String(5),
        doc="The URL key.",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        doc="The creation date.",
        server_default=func.now(),
        nullable=False,
    )
