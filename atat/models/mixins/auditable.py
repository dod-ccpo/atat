from flask import current_app as app
from flask import g
from sqlalchemy import event, inspect

from atat.models.audit_event import AuditEvent
from atat.utils import camel_to_snake, getattr_path

ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete"


class AuditableMixin(object):
    @staticmethod
    def create_audit_event(connection, resource, action, changed_state=None):
        user_id = getattr_path(g, "current_user.id")

        if changed_state is None:
            changed_state = resource.history if action == ACTION_UPDATE else None

        log_data = {
            "user_id": user_id,
            "portfolio_id": resource.portfolio_id,
            "application_id": resource.application_id,
            "resource_type": resource.resource_type,
            "resource_id": resource.id,
            "display_name": resource.displayname,
            "action": action,
            "changed_state": changed_state,
            "event_details": resource.event_details,
        }

        app.logger.info(
            "Audit Event %s",
            action,
            extra={
                "audit_event": {key: str(value) for key, value in log_data.items()},
                "tags": ["audit_event", action],
            },
        )

        if app.config.get("USE_AUDIT_LOG", False):
            audit_event = AuditEvent(**log_data)
            audit_event.save(connection)

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "after_insert", cls.audit_insert)
        event.listen(cls, "after_delete", cls.audit_delete)
        event.listen(cls, "after_update", cls.audit_update)

    @staticmethod
    def audit_insert(mapper, connection, target):
        """Listen for the `after_insert` event and create an AuditLog entry"""
        target.create_audit_event(connection, target, ACTION_CREATE)

    @staticmethod
    def audit_delete(mapper, connection, target):
        """Listen for the `after_delete` event and create an AuditLog entry"""
        target.create_audit_event(connection, target, ACTION_DELETE)

    @staticmethod
    def audit_update(mapper, connection, target):
        if AuditableMixin.get_changes(target):
            target.create_audit_event(connection, target, ACTION_UPDATE)

    def get_changes(self):
        """
        This function returns a dictionary of the form {item: [from_value, to_value]},
        where 'item' is the attribute on the target that has been updated,
        'from_value' is the value of the attribute before it was updated,
        and 'to_value' is the current value of the attribute.

        There may be more than one item in the dictionary, but that is not expected.
        """
        previous_state = {}
        attrs = inspect(self).mapper.column_attrs
        for attr in attrs:
            history = getattr(inspect(self).attrs, attr.key).history
            if history.has_changes():
                deleted = history.deleted.pop() if history.deleted else None
                added = history.added.pop() if history.added else None
                previous_state[attr.key] = [deleted, added]
        return previous_state

    @property
    def history(self):
        return None

    @property
    def event_details(self):
        return None

    @property
    def resource_type(self):
        return camel_to_snake(type(self).__name__)

    @property
    def portfolio_id(self):
        raise NotImplementedError()

    @property
    def application_id(self):
        raise NotImplementedError()

    @property
    def displayname(self):
        return None


def record_permission_sets_updates(instance_state, permission_sets, initiator):
    old_perm_sets = instance_state.attrs.get("permission_sets").value
    if instance_state.persistent and old_perm_sets != permission_sets:
        connection = instance_state.session.connection()
        old_state = [p.name for p in old_perm_sets]
        new_state = [p.name for p in permission_sets]
        changed_state = {"permission_sets": (old_state, new_state)}
        instance_state.object.create_audit_event(
            connection,
            instance_state.object,
            ACTION_UPDATE,
            changed_state=changed_state,
        )
