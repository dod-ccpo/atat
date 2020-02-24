from sqlalchemy.orm.exc import NoResultFound

from atat.database import db
from atat.models.permissions import Permissions
from atat.models.permission_set import PermissionSet
from .exceptions import NotFoundError


class PermissionSets(object):
    VIEW_PORTFOLIO = "view_portfolio"
    VIEW_PORTFOLIO_APPLICATION_MANAGEMENT = "view_portfolio_application_management"
    VIEW_PORTFOLIO_FUNDING = "view_portfolio_funding"
    VIEW_PORTFOLIO_REPORTS = "view_portfolio_reports"
    VIEW_PORTFOLIO_ADMIN = "view_portfolio_admin"
    EDIT_PORTFOLIO_APPLICATION_MANAGEMENT = "edit_portfolio_application_management"
    EDIT_PORTFOLIO_FUNDING = "edit_portfolio_funding"
    EDIT_PORTFOLIO_REPORTS = "edit_portfolio_reports"
    EDIT_PORTFOLIO_ADMIN = "edit_portfolio_admin"
    PORTFOLIO_POC = "portfolio_poc"
    VIEW_AUDIT_LOG = "view_audit_log"
    MANAGE_CCPO_USERS = "manage_ccpo_users"

    VIEW_APPLICATION = "view_application"
    EDIT_APPLICATION_ENVIRONMENTS = "edit_application_environments"
    EDIT_APPLICATION_TEAM = "edit_application_team"
    DELETE_APPLICATION_ENVIRONMENTS = "delete_application_environments"

    @classmethod
    def get(cls, perms_set_name):
        try:
            role = db.session.query(PermissionSet).filter_by(name=perms_set_name).one()
        except NoResultFound:
            raise NotFoundError("permission_set")

        return role

    @classmethod
    def get_all(cls):
        return db.session.query(PermissionSet).all()

    @classmethod
    def get_many(cls, perms_set_names):
        permission_sets = (
            db.session.query(PermissionSet)
            .filter(PermissionSet.name.in_(perms_set_names))
            .all()
        )

        if len(permission_sets) != len(perms_set_names):
            raise NotFoundError("permission_set")

        return permission_sets


ATAT_PERMISSION_SETS = [
    {
        "name": PermissionSets.VIEW_AUDIT_LOG,
        "display_name": "View Audit Log",
        "description": "",
        "permissions": [Permissions.VIEW_AUDIT_LOG],
    },
    {
        "name": PermissionSets.MANAGE_CCPO_USERS,
        "display_name": "View Audit Log",
        "description": "",
        "permissions": [
            Permissions.VIEW_CCPO_USER,
            Permissions.CREATE_CCPO_USER,
            Permissions.EDIT_CCPO_USER,
            Permissions.DELETE_CCPO_USER,
        ],
    },
]

_PORTFOLIO_BASIC_PERMISSION_SETS = [
    {
        "name": PermissionSets.VIEW_PORTFOLIO,
        "description": "View basic portfolio info",
        "display_name": "View Portfolio",
        "permissions": [Permissions.VIEW_PORTFOLIO],
    }
]

_PORTFOLIO_APP_MGMT_PERMISSION_SETS = [
    {
        "name": PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
        "description": "View applications and related resources",
        "display_name": "Application Management",
        "permissions": [
            Permissions.VIEW_APPLICATION,
            Permissions.VIEW_APPLICATION_MEMBER,
            Permissions.VIEW_ENVIRONMENT,
        ],
    },
    {
        "name": PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT,
        "description": "Edit applications and related resources",
        "display_name": "Application Management",
        "permissions": [
            Permissions.EDIT_APPLICATION,
            Permissions.CREATE_APPLICATION,
            Permissions.DELETE_APPLICATION,
            Permissions.EDIT_APPLICATION_MEMBER,
            Permissions.DELETE_APPLICATION_MEMBER,
            Permissions.CREATE_APPLICATION_MEMBER,
            Permissions.EDIT_ENVIRONMENT,
            Permissions.CREATE_ENVIRONMENT,
            Permissions.DELETE_ENVIRONMENT,
            Permissions.ASSIGN_ENVIRONMENT_MEMBER,
        ],
    },
]

_PORTFOLIO_FUNDING_PERMISSION_SETS = [
    {
        "name": PermissionSets.VIEW_PORTFOLIO_FUNDING,
        "description": "View a portfolio's task orders",
        "display_name": "Funding",
        "permissions": [
            Permissions.VIEW_PORTFOLIO_FUNDING,
            Permissions.VIEW_TASK_ORDER_DETAILS,
        ],
    },
    {
        "name": PermissionSets.EDIT_PORTFOLIO_FUNDING,
        "description": "Edit a portfolio's task orders and add new ones",
        "display_name": "Funding",
        "permissions": [
            Permissions.CREATE_TASK_ORDER,
            Permissions.EDIT_TASK_ORDER_DETAILS,
        ],
    },
]

_PORTFOLIO_REPORTS_PERMISSION_SETS = [
    {
        "name": PermissionSets.VIEW_PORTFOLIO_REPORTS,
        "description": "View a portfolio's reports",
        "display_name": "Reporting",
        "permissions": [Permissions.VIEW_PORTFOLIO_REPORTS],
    },
    {
        "name": PermissionSets.EDIT_PORTFOLIO_REPORTS,
        "description": "Edit a portfolio's reports (no-op)",
        "display_name": "Reporting",
        "permissions": [],
    },
]

_PORTFOLIO_ADMIN_PERMISSION_SETS = [
    {
        "name": PermissionSets.VIEW_PORTFOLIO_ADMIN,
        "description": "View a portfolio's admin options",
        "display_name": "Portfolio Administration",
        "permissions": [
            Permissions.VIEW_PORTFOLIO_ADMIN,
            Permissions.VIEW_PORTFOLIO_NAME,
            Permissions.VIEW_PORTFOLIO_USERS,
            Permissions.VIEW_PORTFOLIO_ACTIVITY_LOG,
            Permissions.VIEW_PORTFOLIO_POC,
        ],
    },
    {
        "name": PermissionSets.EDIT_PORTFOLIO_ADMIN,
        "description": "Edit a portfolio's admin options",
        "display_name": "Portfolio Administration",
        "permissions": [
            Permissions.EDIT_PORTFOLIO_NAME,
            Permissions.EDIT_PORTFOLIO_USERS,
            Permissions.CREATE_PORTFOLIO_USERS,
        ],
    },
]

_PORTFOLIO_POC_PERMISSION_SETS = [
    {
        "name": "portfolio_poc",
        "description": "Permissions belonging to the Portfolio POC",
        "display_name": "Portfolio Point of Contact",
        "permissions": [Permissions.EDIT_PORTFOLIO_POC, Permissions.ARCHIVE_PORTFOLIO],
    }
]

PORTFOLIO_PERMISSION_SETS = (
    _PORTFOLIO_BASIC_PERMISSION_SETS
    + _PORTFOLIO_APP_MGMT_PERMISSION_SETS
    + _PORTFOLIO_FUNDING_PERMISSION_SETS
    + _PORTFOLIO_REPORTS_PERMISSION_SETS
    + _PORTFOLIO_ADMIN_PERMISSION_SETS
    + _PORTFOLIO_POC_PERMISSION_SETS
)

_APPLICATION_BASIC_PERMISSION_SET = {
    "name": PermissionSets.VIEW_APPLICATION,
    "description": "View application data",
    "display_name": "View applications",
    "permissions": [
        Permissions.VIEW_APPLICATION,
        Permissions.VIEW_APPLICATION_MEMBER,
        Permissions.VIEW_ENVIRONMENT,
    ],
}

# need perm to assign and unassign users to environments
_APPLICATION_ENVIRONMENTS_PERMISSION_SET = {
    "name": PermissionSets.EDIT_APPLICATION_ENVIRONMENTS,
    "description": "Manage environments for an application",
    "display_name": "Manage environments",
    "permissions": [
        Permissions.EDIT_ENVIRONMENT,
        Permissions.CREATE_ENVIRONMENT,
        Permissions.ASSIGN_ENVIRONMENT_MEMBER,
    ],
}

_APPLICATION_TEAM_PERMISSION_SET = {
    "name": PermissionSets.EDIT_APPLICATION_TEAM,
    "description": "Manage team members for an application",
    "display_name": "Manage team",
    "permissions": [
        Permissions.EDIT_APPLICATION_MEMBER,
        Permissions.DELETE_APPLICATION_MEMBER,
        Permissions.CREATE_APPLICATION_MEMBER,
        Permissions.ASSIGN_ENVIRONMENT_MEMBER,
        Permissions.VIEW_APPLICATION_ACTIVITY_LOG,
    ],
}

_APPLICATION_ENVIRONMENT_DELETE_PERMISSION_SET = {
    "name": PermissionSets.DELETE_APPLICATION_ENVIRONMENTS,
    "description": "Delete environments within an application",
    "display_name": "Delete environments",
    "permissions": [Permissions.DELETE_ENVIRONMENT],
}

APPLICATION_PERMISSION_SETS = [
    _APPLICATION_BASIC_PERMISSION_SET,
    _APPLICATION_TEAM_PERMISSION_SET,
    _APPLICATION_ENVIRONMENTS_PERMISSION_SET,
    _APPLICATION_ENVIRONMENT_DELETE_PERMISSION_SET,
]
