"""enable uuid extension

Revision ID: ff1c9c02fa61
Revises:
Create Date: 2018-07-23 14:54:05.422286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff1c9c02fa61'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')


def downgrade():
    connection = op.get_bind()
    connection.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
