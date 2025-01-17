"""
init2

Revision ID: f32fa217f816
Revises: 71bc198c11bd
Create Date: 2024-03-12 17:51:07.569743

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f32fa217f816"
down_revision = "71bc198c11bd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "urls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("target_url", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("clicks_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_urls")),
    )
    op.create_index(op.f("ix_urls_key"), "urls", ["key"], unique=True)
    op.create_index(
        op.f("ix_urls_target_url"),
        "urls",
        ["target_url"],
        unique=False,
    )
    op.drop_index("ix_url_key", table_name="url")
    op.drop_index("ix_url_target_url", table_name="url")
    op.drop_table("url")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "url",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("key", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "target_url",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.BOOLEAN(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "clicks_count",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_url"),
    )
    op.create_index("ix_url_target_url", "url", ["target_url"], unique=False)
    op.create_index("ix_url_key", "url", ["key"], unique=True)
    op.drop_index(op.f("ix_urls_target_url"), table_name="urls")
    op.drop_index(op.f("ix_urls_key"), table_name="urls")
    op.drop_table("urls")
    # ### end Alembic commands ###
