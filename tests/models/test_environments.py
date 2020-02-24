import pytest

from atat.models import AuditEvent
from atat.models.environment_role import CSPRole
from atat.domain.applications import Applications
from atat.domain.environment_roles import EnvironmentRoles

from tests.factories import *


def test_add_user_to_environment():
    owner = UserFactory.create()
    developer = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    application = Applications.create(
        portfolio.owner,
        portfolio,
        "my test application",
        "It's mine.",
        ["dev", "staging", "prod"],
    )
    dev_environment = application.environments[0]

    application_role = ApplicationRoleFactory.create(
        user=developer, application=application
    )
    EnvironmentRoleFactory.create(
        application_role=application_role,
        environment=dev_environment,
        role=CSPRole.ADMIN,
    )
    assert developer in dev_environment.users


@pytest.mark.audit_log
def test_audit_event_for_environment_deletion(session):
    env = EnvironmentFactory.create(application=ApplicationFactory.create())
    env.deleted = True
    session.add(env)
    session.commit()

    update_event = (
        session.query(AuditEvent)
        .filter(AuditEvent.resource_id == env.id, AuditEvent.action == "update")
        .one()
    )
    assert update_event.changed_state.get("deleted")
    before, after = update_event.changed_state["deleted"]
    assert not before
    assert after


def test_environment_roles_do_not_include_deleted():
    member_list = [
        {"role_name": CSPRole.ADMIN},
        {"role_name": CSPRole.ADMIN},
        {"role_name": CSPRole.ADMIN},
    ]
    env = EnvironmentFactory.create(members=member_list)
    role_1 = env.roles[0]
    role_2 = env.roles[1]

    EnvironmentRoles.delete(role_1.application_role_id, env.id)
    EnvironmentRoles.disable(role_2.id)

    assert len(env.roles) == 2
