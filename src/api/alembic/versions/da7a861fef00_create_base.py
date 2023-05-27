"""
Create base.

Revision ID: da7a861fef00
Revises:
Create Date: 2023-05-24 09:10:15.805765

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "da7a861fef00"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "maillist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_maillist_id"), "maillist", ["id"], unique=False)
    op.create_table(
        "solarpark",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("size_in_sq_m", sa.Float(), nullable=True),
        sa.Column("peak_power", sa.Float(), nullable=True),
        sa.Column("date_of_data", sa.Date(), nullable=True),
        sa.Column("first_detection", sa.Date(), nullable=True),
        sa.Column("last_detection", sa.Date(), nullable=True),
        sa.Column("geometry", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_solarpark_id"), "solarpark", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_solarpark_id"), table_name="solarpark")
    op.drop_table("solarpark")
    op.drop_index(op.f("ix_maillist_id"), table_name="maillist")
    op.drop_table("maillist")
    # ### end Alembic commands ###
