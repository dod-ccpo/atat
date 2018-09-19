from atst.domain.roles import Roles
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions
from atst.domain.users import Users
from atst.domain.workspace_users import WorkspaceUsers
from atst.domain.audit_log import AuditLog

from .query import WorkspacesQuery
from .scopes import ScopedWorkspace


class Workspaces(object):
    @classmethod
    def create(cls, request, name=None):
        name = name or request.id
        workspace = WorkspacesQuery.create(request=request, name=name)
        Workspaces._create_workspace_role(request.creator, workspace, "owner")
        WorkspacesQuery.add_and_commit(workspace)
        AuditLog.log_system_event(workspace, "create workspace")
        return workspace

    @classmethod
    def get(cls, user, workspace_id):
        workspace = WorkspacesQuery.get(workspace_id)
        Authorization.check_workspace_permission(
            user, workspace, Permissions.VIEW_WORKSPACE, "get workspace"
        )

        return ScopedWorkspace(user, workspace)

    @classmethod
    def get_for_update_projects(cls, user, workspace_id):
        workspace = WorkspacesQuery.get(workspace_id)
        Authorization.check_workspace_permission(
            user, workspace, Permissions.ADD_APPLICATION_IN_WORKSPACE, "add project"
        )

        return workspace

    @classmethod
    def get_for_update_information(cls, user, workspace_id):
        workspace = WorkspacesQuery.get(workspace_id)
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.EDIT_WORKSPACE_INFORMATION,
            "update workspace information",
        )

        return workspace

    @classmethod
    def get_by_request(cls, request):
        return WorkspacesQuery.get_by_request(request)

    @classmethod
    def get_with_members(cls, user, workspace_id):
        workspace = WorkspacesQuery.get(workspace_id)
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.VIEW_WORKSPACE_MEMBERS,
            "view workspace members",
        )

        return workspace

    @classmethod
    def for_user(cls, user):
        if Authorization.has_atat_permission(user, Permissions.VIEW_WORKSPACE):
            workspaces = WorkspacesQuery.get_all()
        else:
            workspaces = WorkspacesQuery.get_for_user(user)
        return workspaces

    @classmethod
    def create_member(cls, user, workspace, data):
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            "create workspace member",
        )

        new_user = Users.get_or_create_by_dod_id(
            data["dod_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
        )
        member = Workspaces.add_member(workspace, new_user, data["workspace_role"])
        AuditLog.log_workspace_event(
            user, workspace, member.workspace_role, "create workspace role"
        )
        return member

    @classmethod
    def add_member(cls, workspace, member, role_name):
        workspace_user = WorkspaceUsers.add(member, workspace.id, role_name)
        return workspace_user

    @classmethod
    def update_member(cls, user, workspace, member, role_name):
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            "edit workspace member",
        )
        member = WorkspaceUsers.update_role(member, workspace.id, role_name)
        AuditLog.log_workspace_event(
            user, workspace, member.workspace_role, "update workspace_role"
        )
        return member

    @classmethod
    def _create_workspace_role(cls, user, workspace, role_name):
        role = Roles.get(role_name)
        workspace_role = WorkspacesQuery.create_workspace_role(user, role, workspace)
        WorkspacesQuery.add_and_commit(workspace_role)
        return workspace_role

    @classmethod
    def update(cls, workspace, new_data):
        if "name" in new_data:
            workspace.name = new_data["name"]

        WorkspacesQuery.add_and_commit(workspace)
