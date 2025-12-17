"""initial

Revision ID: 0001
Revises: 
Create Date: 2025-12-17
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ledgers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ledger_id', sa.String(), nullable=False, unique=True),
        sa.Column('input_snapshot', sa.JSON(), nullable=True),
        sa.Column('composite', sa.JSON(), nullable=False),
        sa.Column('robustness', sa.JSON(), nullable=False),
        sa.Column('seals', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'obligations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('obligation_id', sa.String(), nullable=False),
        sa.Column('ledger_id', sa.Integer(), sa.ForeignKey('ledgers.id', ondelete='CASCADE')),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('owner', sa.String(), nullable=True),
        sa.Column('constraint', sa.JSON(), nullable=False),
        sa.Column('premises', sa.JSON(), nullable=True),
        sa.Column('seal_hash', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='unbonded'),
    )


def downgrade():
    op.drop_table('obligations')
    op.drop_table('ledgers')
