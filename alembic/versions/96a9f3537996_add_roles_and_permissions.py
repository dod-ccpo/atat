"""add_roles_and_permissions

Revision ID: 96a9f3537996
Revises: 4ede1e3e50d1
Create Date: 2018-07-30 13:48:31.325234

"""
import os
import sys
from alembic import op
import sqlalchemy as sa

from sqlalchemy.orm.session import Session

from atst.models.role import Role
from atst.models.permissions import Permissions

# revision identifiers, used by Alembic.
revision = '96a9f3537996'
down_revision = '4ede1e3e50d1'
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    roles = [
        Role(
            name='ccpo',
            description='',
            permissions=[
                Permissions.VIEW_ORIGINAL_JEDI_REQEUST,
                Permissions.REVIEW_AND_APPROVE_JEDI_WORKSPACE_REQUEST,
                Permissions.MODIFY_ATAT_ROLE_PERMISSIONS,
                Permissions.CREATE_CSP_ROLE,
                Permissions.DELETE_CSP_ROLE,
                Permissions.DEACTIVE_CSP_ROLE,
                Permissions.MODIFY_CSP_ROLE_PERMISSIONS,

                Permissions.VIEW_USAGE_REPORT,
                Permissions.VIEW_USAGE_DOLLARS,
                Permissions.ADD_AND_ASSIGN_CSP_ROLES,
                Permissions.REMOVE_CSP_ROLES,
                Permissions.REQUEST_NEW_CSP_ROLE,
                Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,

                Permissions.VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS,
                Permissions.VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS,

                Permissions.DEACTIVATE_WORKSPACE,
                Permissions.VIEW_ATAT_PERMISSIONS,
                Permissions.TRANSFER_OWNERSHIP_OF_WORKSPACE,

                Permissions.ADD_APPLICATION_IN_WORKSPACE,
                Permissions.DELETE_APPLICATION_IN_WORKSPACE,
                Permissions.DEACTIVATE_APPLICATION_IN_WORKSPACE,
                Permissions.VIEW_APPLICATION_IN_WORKSPACE,
                Permissions.RENAME_APPLICATION_IN_WORKSPACE,

                Permissions.ADD_ENVIRONMENT_IN_APPLICATION,
                Permissions.DELETE_ENVIRONMENT_IN_APPLICATION,
                Permissions.DEACTIVATE_ENVIRONMENT_IN_APPLICATION,
                Permissions.VIEW_ENVIRONMENT_IN_APPLICATION,
                Permissions.RENAME_ENVIRONMENT_IN_APPLICATION,

                Permissions.ADD_TAG_TO_WORKSPACE,
                Permissions.REMOVE_TAG_FROM_WORKSPACE
            ]
        ),
        Role(
            name='owner',
            description='',
            permissions=[
                Permissions.REQUEST_JEDI_WORKSPACE,
                Permissions.VIEW_ORIGINAL_JEDI_REQEUST,

                Permissions.VIEW_USAGE_REPORT,
                Permissions.VIEW_USAGE_DOLLARS,
                Permissions.ADD_AND_ASSIGN_CSP_ROLES,
                Permissions.REMOVE_CSP_ROLES,
                Permissions.REQUEST_NEW_CSP_ROLE,
                Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,

                Permissions.VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS,
                Permissions.VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS,

                Permissions.DEACTIVATE_WORKSPACE,
                Permissions.VIEW_ATAT_PERMISSIONS,

                Permissions.ADD_APPLICATION_IN_WORKSPACE,
                Permissions.DELETE_APPLICATION_IN_WORKSPACE,
                Permissions.DEACTIVATE_APPLICATION_IN_WORKSPACE,
                Permissions.VIEW_APPLICATION_IN_WORKSPACE,
                Permissions.RENAME_APPLICATION_IN_WORKSPACE,

                Permissions.ADD_ENVIRONMENT_IN_APPLICATION,
                Permissions.DELETE_ENVIRONMENT_IN_APPLICATION,
                Permissions.DEACTIVATE_ENVIRONMENT_IN_APPLICATION,
                Permissions.VIEW_ENVIRONMENT_IN_APPLICATION,
                Permissions.RENAME_ENVIRONMENT_IN_APPLICATION,
            ]
        ),
        Role(
            name='admin',
            description='',
            permissions=[
                Permissions.VIEW_USAGE_REPORT,
                Permissions.ADD_AND_ASSIGN_CSP_ROLES,
                Permissions.REMOVE_CSP_ROLES,
                Permissions.REQUEST_NEW_CSP_ROLE,
                Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,

                Permissions.VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS,
                Permissions.VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS,

                Permissions.ADD_APPLICATION_IN_WORKSPACE,
                Permissions.DELETE_APPLICATION_IN_WORKSPACE,
                Permissions.DEACTIVATE_APPLICATION_IN_WORKSPACE,
                Permissions.VIEW_APPLICATION_IN_WORKSPACE,
                Permissions.RENAME_APPLICATION_IN_WORKSPACE,

                Permissions.ADD_ENVIRONMENT_IN_APPLICATION,
                Permissions.DELETE_ENVIRONMENT_IN_APPLICATION,
                Permissions.DEACTIVATE_ENVIRONMENT_IN_APPLICATION,
                Permissions.VIEW_ENVIRONMENT_IN_APPLICATION,
                Permissions.RENAME_ENVIRONMENT_IN_APPLICATION,
            ]
        ),
        Role(
            name='developer',
            description='',
            permissions=[
                Permissions.VIEW_USAGE_REPORT,
                Permissions.VIEW_USAGE_DOLLARS,
                Permissions.VIEW_APPLICATION_IN_WORKSPACE,
                Permissions.VIEW_ENVIRONMENT_IN_APPLICATION
            ]
        ),
        Role(
            name='billing_auditor',
            description='',
            permissions=[
                Permissions.VIEW_USAGE_REPORT,
                Permissions.VIEW_USAGE_DOLLARS,

                Permissions.VIEW_APPLICATION_IN_WORKSPACE,

                Permissions.VIEW_ENVIRONMENT_IN_APPLICATION,
            ]
        ),
        Role(
            name='security_auditor',
            description='',
            permissions=[
                Permissions.VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS,
                Permissions.VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS,

                Permissions.VIEW_ATAT_PERMISSIONS,

                Permissions.VIEW_APPLICATION_IN_WORKSPACE,

                Permissions.VIEW_ENVIRONMENT_IN_APPLICATION,
            ]
        ),
    ]

    session.add_all(roles)
    session.commit()


def downgrade():
    db = op.get_bind()
    db.execute("""
        DELETE FROM roles
        WHERE name IN (
            'ccpo',
            'owner',
            'admin',
            'developer',
            'billing_auditor',
            'security_auditor'
        );
    """)
