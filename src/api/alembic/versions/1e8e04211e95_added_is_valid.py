"""Added is_valid

Revision ID: 1e8e04211e95
Revises: 347c305e9c12
Create Date: 2023-05-29 16:15:22.014256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e8e04211e95'
down_revision = '347c305e9c12'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('solarpark', sa.Column('is_valid', sa.String(), nullable=True,  server_default="None"))
    op.alter_column('solarpark', 'id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('solarpark', 'is_valid')
    # ### end Alembic commands ###