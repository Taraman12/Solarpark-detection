"""Initial

Revision ID: 8a2e8bbb8ed5
Revises: 
Create Date: 2023-06-26 21:15:20.072652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a2e8bbb8ed5'
down_revision = None
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
    op.create_table('maillist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_maillist_id'), 'maillist', ['id'], unique=False)
    op.create_table('solarpark',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name_of_model', sa.String(), nullable=True),
    sa.Column('size_in_sq_m', sa.Float(), nullable=True),
    sa.Column('peak_power', sa.Float(), nullable=True),
    sa.Column('date_of_data', sa.Date(), nullable=True),
    sa.Column('first_detection', sa.Date(), nullable=True),
    sa.Column('last_detection', sa.Date(), nullable=True),
    sa.Column('avg_confidence', sa.Float(), nullable=True),
    sa.Column('name_in_aws', sa.String(), nullable=True),
    sa.Column('is_valid', sa.String(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('lat', sa.ARRAY(sa.Float()), nullable=True),
    sa.Column('lon', sa.ARRAY(sa.Float()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_solarpark_id'), 'solarpark', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_solarpark_id'), table_name='solarpark')
    op.drop_table('solarpark')
    op.drop_index(op.f('ix_maillist_id'), table_name='maillist')
    op.drop_table('maillist')
    op.drop_index(op.f('ix_instance_id'), table_name='instance')
    op.drop_table('instance')
    # ### end Alembic commands ###
