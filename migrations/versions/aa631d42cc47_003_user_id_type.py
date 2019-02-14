"""003_user_id_type

Revision ID: aa631d42cc47
Revises: 701ddf864730
Create Date: 2019-01-30 13:16:45.249162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa631d42cc47'
down_revision = '701ddf864730'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE "user" DROP CONSTRAINT "user_pkey" CASCADE')
    op.alter_column('user', 'identity', existing_type=sa.Integer(), type_=sa.String())
    op.alter_column('case', 'assigned_staff_id', existing_type=sa.Integer(), type_=sa.String())
    op.alter_column('case', 'client_id', existing_type=sa.Integer(), type_=sa.String())
    op.alter_column('case', 'counterparty_conveyancer_contact_id', existing_type=sa.Integer(), type_=sa.String())
    op.alter_column('case', 'counterparty_id', existing_type=sa.Integer(), type_=sa.String())
    op.create_primary_key('user_pkey', 'user', ['identity'])


def downgrade():
    op.execute('ALTER TABLE "user" DROP CONSTRAINT "user_pkey" CASCADE')    
    op.alter_column('user', 'identity', existing_type=sa.String(), type_=sa.Integer(), postgresql_using="identity::integer", autoincrement=True)
    op.alter_column('case', 'assigned_staff_id', existing_type=sa.String(), type_=sa.Integer(), postgresql_using="identity::integer", autoincrement=True)
    op.alter_column('case', 'client_id', existing_type=sa.String(), type_=sa.Integer(), postgresql_using="identity::integer", autoincrement=True)
    op.alter_column('case', 'counterparty_conveyancer_contact_id', existing_type=sa.String(), type_=sa.Integer(), postgresql_using="identity::integer", autoincrement=True)
    op.alter_column('case', 'counterparty_id', existing_type=sa.String(), type_=sa.Integer(), postgresql_using="identity::integer", autoincrement=True)
    op.create_primary_key('user_pkey', 'user', ['identity'])
