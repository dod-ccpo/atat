import pytest
import pendulum

from atat.domain.environments import Environments
from atat.domain.portfolios import Portfolios
from atat.domain.portfolio_roles import PortfolioRoles
from atat.domain.applications import Applications
from atat.domain.permission_sets import PermissionSets
from atat.models import AuditEvent, InvitationStatus, PortfolioRoleStatus, CSPRole

from tests.factories import *
from atat.domain.portfolio_roles import PortfolioRoles


@pytest.mark.audit_log
def test_has_no_portfolio_role_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    portfolio_role = PortfolioRoles.add(user, portfolio.id)
    create_event = (
        session.query(AuditEvent)
        .filter(
            AuditEvent.resource_id == portfolio_role.id, AuditEvent.action == "create"
        )
        .one()
    )

    assert not create_event.changed_state


@pytest.mark.audit_log
def test_has_portfolio_role_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    # in order to get the history, we don't want the PortfolioRoleFactory
    #  to commit after create()
    # PortfolioRoleFactory._meta.sqlalchemy_session_persistence = "flush"
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, permission_sets=[]
    )
    PortfolioRoles.update(
        portfolio_role, PortfolioRoles.DEFAULT_PORTFOLIO_PERMISSION_SETS
    )

    changed_event = (
        session.query(AuditEvent)
        .filter(
            AuditEvent.resource_id == portfolio_role.id, AuditEvent.action == "update"
        )
        .one()
    )
    old_state, new_state = changed_event.changed_state["permission_sets"]
    assert old_state == []
    assert set(new_state) == PortfolioRoles.DEFAULT_PORTFOLIO_PERMISSION_SETS


@pytest.mark.audit_log
def test_has_portfolio_status_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    # in order to get the history, we don't want the PortfolioRoleFactory
    #  to commit after create()
    PortfolioRoleFactory._meta.sqlalchemy_session_persistence = "flush"
    portfolio_role = PortfolioRoleFactory.create(portfolio=portfolio, user=user)
    portfolio_role.status = PortfolioRoleStatus.ACTIVE
    session.add(portfolio_role)
    session.commit()

    changed_events = (
        session.query(AuditEvent)
        .filter(
            AuditEvent.resource_id == portfolio_role.id, AuditEvent.action == "update"
        )
        .all()
    )

    # changed_state["status"] returns a list [previous status, current status]
    assert changed_events[0].changed_state["status"][0] == "pending"
    assert changed_events[0].changed_state["status"][1] == "active"


@pytest.mark.audit_log
def test_has_no_env_role_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=owner)
    application = ApplicationFactory.create(portfolio=portfolio)
    environment = EnvironmentFactory.create(
        application=application, name="new environment!"
    )

    app_role = ApplicationRoleFactory.create(user=user, application=application)
    env_role = EnvironmentRoleFactory.create(
        application_role=app_role, environment=environment, role="developer"
    )
    create_event = (
        session.query(AuditEvent)
        .filter(AuditEvent.resource_id == env_role.id, AuditEvent.action == "create")
        .one()
    )

    assert not create_event.changed_state


@pytest.mark.audit_log
def test_has_env_role_history(session):
    user = UserFactory.create()
    application = ApplicationFactory.create()
    app_role = ApplicationRoleFactory.create(user=user, application=application)
    environment = EnvironmentFactory.create(
        application=application, name="new environment!"
    )

    env_role = EnvironmentRoleFactory.create(
        application_role=app_role, environment=environment, role="developer"
    )
    session.add(env_role)
    session.commit()
    session.refresh(env_role)

    env_role.role = "admin"
    session.add(env_role)
    session.commit()

    changed_events = (
        session.query(AuditEvent)
        .filter(AuditEvent.resource_id == env_role.id, AuditEvent.action == "update")
        .all()
    )
    # changed_state["role"] returns a list [previous role, current role]
    assert changed_events[0].changed_state["role"][0] == "developer"
    assert changed_events[0].changed_state["role"][1] == "admin"


def test_event_details():
    owner = UserFactory.create()
    user = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    portfolio_role = PortfolioRoles.add(user, portfolio.id)

    assert portfolio_role.event_details["updated_user_name"] == user.displayname
    assert portfolio_role.event_details["updated_user_id"] == str(user.id)


def test_status_when_member_is_active():
    portfolio_role = PortfolioRoleFactory.create(status=PortfolioRoleStatus.ACTIVE)
    assert portfolio_role.display_status == "active"


def test_status_when_member_is_disabled():
    portfolio_role = PortfolioRoleFactory.create(status=PortfolioRoleStatus.DISABLED)
    assert portfolio_role.display_status == "disabled"


def test_status_when_invitation_has_been_rejected_for_expirations():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    PortfolioInvitationFactory.create(
        role=portfolio_role, status=InvitationStatus.REJECTED_EXPIRED
    )
    assert portfolio_role.display_status == "invite_expired"


def test_status_when_invitation_has_been_rejected_for_wrong_user():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    PortfolioInvitationFactory.create(
        role=portfolio_role, status=InvitationStatus.REJECTED_WRONG_USER
    )
    assert portfolio_role.display_status == "invite_error"


def test_status_when_invitation_has_been_revoked():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    PortfolioInvitationFactory.create(
        role=portfolio_role, status=InvitationStatus.REVOKED
    )
    assert portfolio_role.display_status == "invite_revoked"


def test_status_when_invitation_is_expired():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    PortfolioInvitationFactory.create(
        role=portfolio_role,
        status=InvitationStatus.PENDING,
        expiration_time=pendulum.now(tz="utc").subtract(seconds=1),
    )
    assert portfolio_role.display_status == "invite_expired"


def test_can_not_resend_invitation_if_active():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    PortfolioInvitationFactory.create(
        role=portfolio_role, status=InvitationStatus.ACCEPTED
    )
    assert not portfolio_role.can_resend_invitation


def test_can_resend_invitation_if_expired():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    PortfolioInvitationFactory.create(
        role=portfolio_role, status=InvitationStatus.REJECTED_EXPIRED
    )
    assert portfolio_role.can_resend_invitation


def test_can_list_all_environments():
    portfolio = PortfolioFactory.create(
        applications=[
            {
                "name": "application1",
                "environments": [
                    {"name": "dev"},
                    {"name": "staging"},
                    {"name": "prod"},
                ],
            },
            {
                "name": "application2",
                "environments": [
                    {"name": "dev"},
                    {"name": "staging"},
                    {"name": "prod"},
                ],
            },
            {
                "name": "application3",
                "environments": [
                    {"name": "dev"},
                    {"name": "staging"},
                    {"name": "prod"},
                ],
            },
        ]
    )

    assert len(portfolio.all_environments) == 9


def test_can_list_all_permissions():
    role_one = PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING)
    role_two = PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_REPORTS)
    port_role = PortfolioRoleFactory.create(permission_sets=[role_one, role_two])
    expected_perms = role_one.permissions + role_two.permissions
    assert expected_perms == expected_perms


def test_has_permission_set():
    perm_sets = PermissionSets.get_many(
        [PermissionSets.VIEW_PORTFOLIO_FUNDING, PermissionSets.VIEW_PORTFOLIO_REPORTS]
    )
    port_role = PortfolioRoleFactory.create(permission_sets=perm_sets)

    assert port_role.has_permission_set(PermissionSets.VIEW_PORTFOLIO_REPORTS)


def test_does_not_have_permission_set():
    perm_sets = PermissionSets.get_many(
        [PermissionSets.VIEW_PORTFOLIO_FUNDING, PermissionSets.VIEW_PORTFOLIO_REPORTS]
    )
    port_role = PortfolioRoleFactory.create(permission_sets=perm_sets)

    assert not port_role.has_permission_set(
        PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT
    )
