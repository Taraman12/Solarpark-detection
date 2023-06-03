"""Added instance

Revision ID: 2b672256b976
Revises: 34a2b4eb9563
Create Date: 2023-06-02 15:14:12.663238

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b672256b976'
down_revision = '34a2b4eb9563'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('instance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('service', sa.String(), nullable=True),
    sa.Column('ec2_instance_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('service')
    )
    op.create_index(op.f('ix_instance_id'), 'instance', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_instance_id'), table_name='instance')
    op.drop_table('instance')
    # ### end Alembic commands ###
