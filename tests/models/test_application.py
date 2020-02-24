import pytest

from atat.domain.application_roles import ApplicationRoles
from atat.models import ApplicationRoleStatus
from atat.models import AuditEvent

from tests.factories import (
    ApplicationFactory,
    ApplicationRoleFactory,
    EnvironmentFactory,
    UserFactory,
)


def test_application_environments_excludes_deleted():
    app = ApplicationFactory.create()
    env = EnvironmentFactory.create(application=app)
    EnvironmentFactory.create(application=app, deleted=True)
    assert len(app.environments) == 1
    assert app.environments[0].id == env.id


def test_application_members_excludes_deleted(session):
    app = ApplicationFactory.create()
    member_role = ApplicationRoleFactory.create(
        application=app, status=ApplicationRoleStatus.ACTIVE
    )
    disabled_role = ApplicationRoleFactory.create(
        application=app, status=ApplicationRoleStatus.DISABLED
    )
    disabled_role.deleted = True
    session.add(disabled_role)
    session.commit()

    assert len(app.members) == 1
    assert app.members[0].id == member_role.id


@pytest.mark.audit_log
def test_audit_event_for_application_deletion(session):
    app = ApplicationFactory.create()
    app.deleted = True
    session.add(app)
    session.commit()

    update_event = (
        session.query(AuditEvent)
        .filter(AuditEvent.resource_id == app.id, AuditEvent.action == "update")
        .one()
    )
    assert update_event.changed_state.get("deleted")
    assert update_event.changed_state["deleted"] == [False, True]
