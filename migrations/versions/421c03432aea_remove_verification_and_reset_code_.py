"""Remove verification and reset code fields

Revision ID: 421c03432aea
Revises: 
Create Date: 2024-12-03 12:28:51.375355

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '421c03432aea'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_verified')
        batch_op.drop_column('reset_code_expires')
        batch_op.drop_column('verification_code_expires')
        batch_op.drop_column('reset_code')
        batch_op.drop_column('verification_code')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('verification_code', sa.VARCHAR(length=6), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('reset_code', sa.VARCHAR(length=6), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('verification_code_expires', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('reset_code_expires', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('is_verified', sa.BOOLEAN(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###