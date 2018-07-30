from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.dialects.postgresql import insert

from atst.models.workspace_role import WorkspaceRole
from atst.models.workspace_user import WorkspaceUser
from atst.models.user import User
from .roles import Roles
from .users import Users
from .exceptions import NotFoundError

class WorkspaceUsers(object):

    def __init__(self, db_session):
        self.db_session = db_session
        self.roles_repo = Roles(db_session)
        self.users_repo = Users(db_session)

    def get(self, workspace_id, user_id):
        try:
            user = self.users_repo.get(user_id)
        except NoResultFound:
            raise NotFoundError("user")

        try:
            workspace_role = (
                WorkspaceRole.query.join(User)
                .filter(User.id == user_id, WorkspaceRole.workspace_id == workspace_id)
                .one()
            )
        except NoResultFound:
            workspace_role = None

        return WorkspaceUser(user, workspace_role)

    def add_many(self, workspace_id, workspace_user_dicts):
        workspace_users = []

        for user_dict in workspace_user_dicts:
            try:
                user = self.users_repo.get(user_dict["id"])
            except NoResultFound:
                default_role = self.roles_repo.get("developer")
                user = User(id=user_dict["id"], atat_role=default_role)

            try:
                role = self.roles_repo.get(user_dict["workspace_role"])
            except NoResultFound:
                raise NotFoundError("role")

            try:
                existing_workspace_role = self.db_session.query(WorkspaceRole).filter(
                    WorkspaceRole.user == user,
                    WorkspaceRole.workspace_id == workspace_id,
                ).one()
                new_workspace_role = existing_workspace_role
                new_workspace_role.role = role
            except NoResultFound:
                new_workspace_role = WorkspaceRole(
                    user=user, role_id=role.id, workspace_id=workspace_id
                )

            user.workspace_roles.append(new_workspace_role)
            workspace_user = WorkspaceUser(user, new_workspace_role)
            workspace_users.append(workspace_user)

            self.db_session.add(user)

        self.db_session.commit()

        return workspace_users
