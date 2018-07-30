"""add_default_atat_role

Revision ID: 4ea5917e7781
Revises: 96a9f3537996
Create Date: 2018-07-30 13:51:29.576931

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import Session


# revision identifiers, used by Alembic.
revision = '4ea5917e7781'
down_revision = '96a9f3537996'
branch_labels = None
depends_on = None

from atst.models.role import Role
from atst.models.permissions import Permissions


def upgrade():
    session = Session(bind=op.get_bind())
    mission_owner_role = Role(
        name='default',
        description='',
        permissions=[
            Permissions.REQUEST_JEDI_WORKSPACE,
        ]
    )
    session.add(mission_owner_role)
    session.commit()


def downgrade():
    db = op.get_bind()
    db.execute("DELETE FROM roles WHERE name = 'default'")

