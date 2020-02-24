import pytest

from atat.domain.applications import Applications
from atat.domain.audit_log import AuditLog
from atat.domain.exceptions import UnauthorizedError
from atat.domain.permission_sets import PermissionSets
from atat.domain.portfolios import Portfolios
from atat.domain.users import Users
from atat.models.portfolio_role import Status as PortfolioRoleStatus
from tests.factories import (
    ApplicationFactory,
    ApplicationInvitationFactory,
    ApplicationRoleFactory,
    EnvironmentFactory,
    EnvironmentRoleFactory,
    PortfolioFactory,
    PortfolioRoleFactory,
    UserFactory,
)


@pytest.fixture(scope="function")
def ccpo():
    return UserFactory.create_ccpo()


@pytest.fixture(scope="function")
def developer():
    return UserFactory.create()


@pytest.mark.audit_log
def test_paginate_audit_log():
    user = UserFactory.create()
    for _ in range(100):
        AuditLog.log_system_event(user, action="create")

    events = AuditLog.get_all_events(pagination_opts={"per_page": 25, "page": 2})
    assert len(events) == 25


@pytest.mark.audit_log
def test_paginate_ws_audit_log():
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)
    for _ in range(100):
        AuditLog.log_system_event(
            resource=application, action="create", portfolio=portfolio
        )

    events = AuditLog.get_portfolio_events(
        portfolio, pagination_opts={"per_page": 25, "page": 2}
    )
    assert len(events) == 25


@pytest.mark.audit_log
def test_portfolio_audit_log_only_includes_current_portfolio_events():
    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=owner)
    other_portfolio = PortfolioFactory.create(owner=owner)
    # Add some audit events
    application_1 = ApplicationFactory.create(portfolio=portfolio)
    application_2 = ApplicationFactory.create(portfolio=other_portfolio)

    events = AuditLog.get_portfolio_events(portfolio)
    for event in events:
        assert event.portfolio_id == portfolio.id
        assert (
            not event.portfolio_id == other_portfolio.id
            or event.resource_id == other_portfolio.id
        )


@pytest.mark.audit_log
def test_get_portfolio_events_includes_app_and_env_events():
    owner = UserFactory.create()
    # add portfolio level events
    portfolio = PortfolioFactory.create(owner=owner)
    portfolio_events = AuditLog.get_portfolio_events(portfolio)

    # add application level events
    application = ApplicationFactory.create(portfolio=portfolio)
    Applications.update(application, {"name": "Star Cruiser"})
    app_role = ApplicationRoleFactory.create(application=application)
    app_invite = ApplicationInvitationFactory.create(role=app_role)
    portfolio_and_app_events = AuditLog.get_portfolio_events(portfolio)
    assert len(portfolio_events) < len(portfolio_and_app_events)

    # add environment level events
    env = EnvironmentFactory.create(application=application)
    env_role = EnvironmentRoleFactory.create(environment=env, application_role=app_role)
    portfolio_app_and_env_events = AuditLog.get_portfolio_events(portfolio)
    assert len(portfolio_and_app_events) < len(portfolio_app_and_env_events)

    resource_types = [event.resource_type for event in portfolio_app_and_env_events]
    assert "application" in resource_types
    assert "application_role" in resource_types
    assert "application_invitation" in resource_types
    assert "environment" in resource_types
    assert "environment_role" in resource_types


@pytest.mark.audit_log
def test_get_application_events():
    # add in some portfolio level events
    portfolio = PortfolioFactory.create()
    Portfolios.update(portfolio, {"name": "New Name"})
    # add app level events
    application = ApplicationFactory.create(portfolio=portfolio)
    Applications.update(application, {"name": "Star Cruiser"})
    app_role = ApplicationRoleFactory.create(application=application)
    app_invite = ApplicationInvitationFactory.create(role=app_role)
    env = EnvironmentFactory.create(application=application)
    env_role = EnvironmentRoleFactory.create(environment=env, application_role=app_role)
    # add rando app
    rando_app = ApplicationFactory.create(portfolio=portfolio)

    events = AuditLog.get_application_events(application)
    for event in events:
        assert event.application_id == application.id
        assert not event.application_id == rando_app.id

    resource_types = [event.resource_type for event in events]
    assert "portfolio" not in resource_types


@pytest.mark.audit_log
def test_get_all_includes_ccpo_user_changes():
    user = UserFactory.create()
    initial_audit_log = AuditLog.get_all_events()
    Users.give_ccpo_perms(user)
    Users.revoke_ccpo_perms(user)

    assert len(AuditLog.get_all_events()) == len(initial_audit_log) + 2
