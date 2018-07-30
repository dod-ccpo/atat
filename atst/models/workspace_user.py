class WorkspaceUser(object):
    def __init__(self, user, workspace_role):
        self.user = user
        self.workspace_role = workspace_role

    def permissions(self):
        atat_permissions = set(self.user.atat_role.permissions)
        workspace_permissions = (
            [] if self.workspace_role is None else self.workspace_role.role.permissions
        )
        return set(workspace_permissions).union(atat_permissions)

    def workspace_id(self):
        return self.workspace_role.workspace_id
