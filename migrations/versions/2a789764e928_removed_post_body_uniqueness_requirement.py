"""Removed post body uniqueness requirement

Revision ID: 2a789764e928
Revises: 60f9d6bc51c1
Create Date: 2022-12-13 01:40:12.414671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a789764e928'
down_revision = '60f9d6bc51c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('salt',
               existing_type=sa.VARCHAR(length=16),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('salt',
               existing_type=sa.VARCHAR(length=16),
               nullable=True)

    # ### end Alembic commands ###