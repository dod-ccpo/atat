from atst.database import db
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole, CSPRole
from atst.models.project import Project
from atst.domain.audit_log import AuditLog


class Environments(object):
    @classmethod
    def create_many(cls, user, project, names):
        for name in names:
            Environments._create(user, project, name)

    @classmethod
    def add_member(cls, user, environment, member, role=CSPRole.NONSENSE_ROLE):
        environment_role = EnvironmentRole(
            user=member, environment=environment, role=role.value
        )
        db.session.add(environment_role)
        db.session.commit()

        AuditLog.log_workspace_event(
            user,
            environment.project.workspace,
            environment_role,
            "add environment role",
        )

        return environment

    @classmethod
    def for_user(cls, user, project):
        return (
            db.session.query(Environment)
            .join(EnvironmentRole)
            .join(Project)
            .filter(EnvironmentRole.user_id == user.id)
            .filter(Project.id == Environment.project_id)
            .all()
        )

    @classmethod
    def _create(cls, user, project, name):
        environment = Environment(project=project, name=name)
        db.session.add(environment)
        db.session.commit()
        AuditLog.log_workspace_event(
            user, project.workspace, environment, "create environment"
        )
        return environment
