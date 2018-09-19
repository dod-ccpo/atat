from atst.database import db
from atst.domain.common import Query
from atst.domain.authz import Authorization, Permissions
from atst.models.audit_event import AuditEvent


class AuditEventQuery(Query):
    model = AuditEvent

    @classmethod
    def get_all(cls):
        return db.session.query(cls.model).order_by(cls.model.time_created.desc()).all()


class AuditLog(object):
    @classmethod
    def log_event(cls, user, resource, action):
        return cls._log(user=user, resource=resource, action=action)

    @classmethod
    def log_workspace_event(cls, user, workspace, resource, action):
        return cls._log(
            user=user, workspace_id=workspace.id, resource=resource, action=action
        )

    @classmethod
    def log_system_event(cls, resource, action):
        return cls._log(resource=resource, action=action)

    @classmethod
    def get_all_events(cls, user):
        Authorization.check_atat_permission(
            user, Permissions.VIEW_AUDIT_LOG, "view audit log"
        )
        return AuditEventQuery.get_all()

    @classmethod
    def _resource_name(cls, resource):
        return type(resource).__name__.lower()

    @classmethod
    def _log(cls, user=None, workspace_id=None, resource=None, action=None):
        resource_id = resource.id if resource else None
        resource_name = cls._resource_name(resource) if resource else None

        audit_event = AuditEventQuery.create(
            user=user,
            workspace_id=workspace_id,
            resource_id=resource_id,
            resource_name=resource_name,
            action=action,
        )
        return AuditEventQuery.add_and_commit(audit_event)
