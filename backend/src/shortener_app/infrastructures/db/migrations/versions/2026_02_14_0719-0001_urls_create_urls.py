"""create_urls

Revision ID: 0001_urls
Revises:
Create Date: 2026-02-14 07:19:27.919216+00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_urls"
down_revision = None
branch_labels = ("baseline",)
depends_on = None


def upgrade() -> None:
    op.create_table(
        "urls",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=True),
        sa.Column("key", sa.String(length=5), nullable=False),
        sa.Column("target_url", sa.String(length=2048), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("clicks_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_used", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_urls")),
    )
    op.create_index(op.f("ix_urls_key"), "urls", ["key"], unique=True)
    op.create_index(op.f("ix_urls_user_id"), "urls", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_urls_user_id"), table_name="urls")
    op.drop_index(op.f("ix_urls_key"), table_name="urls")
    op.drop_table("urls")
