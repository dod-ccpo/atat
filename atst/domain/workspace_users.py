from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.workspace_role import WorkspaceRole
from atst.models.workspace_user import WorkspaceUser
from atst.models.user import User

from .roles import Roles
from .exceptions import NotFoundError


class WorkspaceUsers(object):
    @classmethod
    def get(cls, workspace_id, user_id):
        user = cls._get_user(user_id)

        try:
            workspace_role = (
                db.session.query(WorkspaceRole)
                .join(User)
                .filter(User.id == user_id, WorkspaceRole.workspace_id == workspace_id)
                .one()
            )
        except NoResultFound:
            workspace_role = None

        return WorkspaceUser(user, workspace_role)

    @classmethod
    def _get_workspace_role(cls, user, workspace_id):
        try:
            existing_workspace_role = (
                db.session.query(WorkspaceRole)
                .filter(
                    WorkspaceRole.user == user,
                    WorkspaceRole.workspace_id == workspace_id,
                )
                .one()
            )
            return existing_workspace_role
        except NoResultFound:
            raise NotFoundError("workspace role")

    @classmethod
    def add(cls, user, workspace_id, role_name):
        role = Roles.get(role_name)

        new_workspace_role = None
        try:
            existing_workspace_role = (
                db.session.query(WorkspaceRole)
                .filter(
                    WorkspaceRole.user == user,
                    WorkspaceRole.workspace_id == workspace_id,
                )
                .one()
            )
            new_workspace_role = existing_workspace_role
            new_workspace_role.role = role
        except NoResultFound:
            new_workspace_role = WorkspaceRole(
                user=user, role_id=role.id, workspace_id=workspace_id
            )

        user.workspace_roles.append(new_workspace_role)
        db.session.add(user)
        db.session.commit()

        return WorkspaceUser(user, new_workspace_role)

    @classmethod
    def update_role(cls, member, workspace_id, role_name):
        new_role = Roles.get(role_name)
        workspace_role = WorkspaceUsers._get_workspace_role(member.user, workspace_id)
        workspace_role.role = new_role

        db.session.add(workspace_role)
        db.session.commit()
        return WorkspaceUser(member.user, workspace_role)

    @classmethod
    def add_many(cls, workspace_id, workspace_user_dicts):
        workspace_users = []

        for user_dict in workspace_user_dicts:
            try:
                user = cls._get_user(user_dict["id"])
            except NoResultFound:
                default_role = Roles.get("developer")
                user = User(id=user_dict["id"], atat_role=default_role)

            try:
                role = Roles.get(user_dict["workspace_role"])
            except NoResultFound:
                raise NotFoundError("role")

            try:
                existing_workspace_role = (
                    db.session.query(WorkspaceRole)
                    .filter(
                        WorkspaceRole.user == user,
                        WorkspaceRole.workspace_id == workspace_id,
                    )
                    .one()
                )
                new_workspace_role = existing_workspace_role
                new_workspace_role.role = role
            except NoResultFound:
                new_workspace_role = WorkspaceRole(
                    user=user, role_id=role.id, workspace_id=workspace_id
                )

            user.workspace_roles.append(new_workspace_role)
            workspace_user = WorkspaceUser(user, new_workspace_role)
            workspace_users.append(workspace_user)

            db.session.add(user)

        db.session.commit()

        return workspace_users

    @classmethod
    def _get_user(cls, id_):
        try:
            user = db.session.query(User).filter_by(id=id_).one()
        except NoResultFound:
            raise NotFoundError("user")
        return user
