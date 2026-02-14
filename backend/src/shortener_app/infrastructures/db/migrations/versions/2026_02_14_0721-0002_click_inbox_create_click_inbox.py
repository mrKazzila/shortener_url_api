"""create_click_inbox

Revision ID: 0002_click_inbox
Revises: 0001_urls
Create Date: 2026-02-14 07:21:01.057596+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_click_inbox"
down_revision = "0001_urls"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "click_inbox",
        sa.Column("event_id", sa.UUID(), nullable=False),
        sa.Column("url_key", sa.String(length=5), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("event_id", name=op.f("pk_click_inbox")),
    )


def downgrade() -> None:
    op.drop_table("click_inbox")
