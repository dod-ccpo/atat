from unittest.mock import Mock

import pytest

from atat.domain.permission_sets import PermissionSets
from atat.models import Permissions
from atat.utils.context_processors import get_resources_from_context
from atat.utils.context_processors import portfolio as portfolio_context
from atat.utils.context_processors import user_can_view
from tests.factories import *


def test_get_resources_from_context():
    portfolio = PortfolioFactory.create()
    task_order = TaskOrderFactory.create(portfolio=portfolio)
    application = ApplicationFactory.create(portfolio=portfolio)
    environment = EnvironmentFactory.create(application=application)

    assert get_resources_from_context({"portfolio_id": portfolio.id}) == (portfolio,)
    assert get_resources_from_context({"application_id": application.id}) == (
        portfolio,
        application,
    )
    assert get_resources_from_context({"environment_id": environment.id}) == (
        portfolio,
        application,
    )
    assert get_resources_from_context({"task_order_id": task_order.id}) == (
        portfolio,
        task_order,
    )


@pytest.fixture
def set_g(monkeypatch):
    _g = Mock()
    monkeypatch.setattr("atat.utils.context_processors.g", _g)

    def _set_g(attr, val):
        setattr(_g, attr, val)

    yield _set_g


def test_user_can_view(set_g):
    owner = UserFactory.create()
    app_user = UserFactory.create()
    rando = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    application = ApplicationFactory.create(portfolio=portfolio)
    ApplicationRoleFactory.create(
        user=app_user,
        application=application,
        permission_sets=PermissionSets.get_many([PermissionSets.VIEW_APPLICATION]),
    )

    set_g("portfolio", portfolio)
    set_g("application", application)
    set_g("current_user", owner)
    assert user_can_view(Permissions.VIEW_APPLICATION)

    set_g("current_user", app_user)
    assert user_can_view(Permissions.VIEW_APPLICATION)

    set_g("current_user", rando)
    assert not user_can_view(Permissions.VIEW_APPLICATION)


def test_portfolio_no_user(set_g):
    set_g("current_user", None)
    assert portfolio_context() == {}


def test_portfolio_with_user(set_g):
    user = UserFactory.create()
    set_g("current_user", user)
    set_g("portfolio", None)
    assert portfolio_context() != {}
