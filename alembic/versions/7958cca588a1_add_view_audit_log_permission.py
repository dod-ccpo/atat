"""add view_audit_log permission

Revision ID: 7958cca588a1
Revises: 875841fac207
Create Date: 2018-09-14 10:20:20.016575

"""
from alembic import op
from sqlalchemy.orm.session import Session

from atst.models.role import Role
from atst.models.permissions import Permissions


# revision identifiers, used by Alembic.
revision = '7958cca588a1'
down_revision = '875841fac207'
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    admin_roles = session.query(Role).filter(Role.name.in_(["ccpo", "security_auditor"])).all()
    for role in admin_roles:
        role.add_permission(Permissions.VIEW_AUDIT_LOG)
        session.add(role)

    session.commit()


def downgrade():
    session = Session(bind=op.get_bind())
    admin_roles = session.query(Role).filter(Role.name.in_(["ccpo", "security_auditor"])).all()
    for role in admin_roles:
        role.remove_permission(Permissions.VIEW_AUDIT_LOG)
        session.add(role)

    session.commit()
