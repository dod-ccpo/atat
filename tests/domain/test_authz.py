import pytest

from tests.factories import (
    ApplicationRoleFactory,
    TaskOrderFactory,
    UserFactory,
    PortfolioFactory,
    PortfolioRoleFactory,
)
from atat.domain.authz import Authorization, user_can_access
from atat.domain.authz.decorator import user_can_access_decorator
from atat.domain.permission_sets import PermissionSets
from atat.domain.exceptions import UnauthorizedError
from atat.models.permissions import Permissions
from atat.domain.portfolio_roles import PortfolioRoles

from tests.utils import FakeLogger


@pytest.fixture
def invalid_user():
    return UserFactory.create()


@pytest.fixture
def task_order():
    return TaskOrderFactory.create()


def test_has_portfolio_permission():
    role_one = PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING)
    role_two = PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_REPORTS)
    port_role = PortfolioRoleFactory.create(permission_sets=[role_one, role_two])
    different_user = UserFactory.create()
    assert Authorization.has_portfolio_permission(
        port_role.user, port_role.portfolio, Permissions.VIEW_PORTFOLIO_REPORTS
    )
    assert not Authorization.has_portfolio_permission(
        port_role.user, port_role.portfolio, Permissions.CREATE_TASK_ORDER
    )
    assert not Authorization.has_portfolio_permission(
        different_user, port_role.portfolio, Permissions.VIEW_PORTFOLIO_REPORTS
    )


def test_has_application_permission():
    role_one = PermissionSets.get(PermissionSets.EDIT_APPLICATION_TEAM)
    role_two = PermissionSets.get(PermissionSets.EDIT_APPLICATION_ENVIRONMENTS)
    app_role = ApplicationRoleFactory.create(permission_sets=[role_one, role_two])
    different_user = UserFactory.create()
    assert Authorization.has_application_permission(
        app_role.user, app_role.application, Permissions.EDIT_ENVIRONMENT
    )
    assert not Authorization.has_portfolio_permission(
        app_role.user, app_role.application, Permissions.DELETE_ENVIRONMENT
    )
    assert not Authorization.has_portfolio_permission(
        different_user, app_role.application, Permissions.DELETE_ENVIRONMENT
    )


def test_user_can_access():
    ccpo = UserFactory.create_ccpo()
    edit_admin = UserFactory.create()
    view_admin = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=edit_admin)
    # factory gives view perms by default
    view_admin_pr = PortfolioRoleFactory.create(user=view_admin, portfolio=portfolio)

    # check a site-wide permission
    assert user_can_access(ccpo, Permissions.VIEW_AUDIT_LOG)

    with pytest.raises(UnauthorizedError):
        user_can_access(edit_admin, Permissions.VIEW_AUDIT_LOG)

    with pytest.raises(UnauthorizedError):
        user_can_access(view_admin, Permissions.VIEW_AUDIT_LOG)

    # check a portfolio view permission
    assert user_can_access(ccpo, Permissions.VIEW_PORTFOLIO, portfolio=portfolio)
    assert user_can_access(edit_admin, Permissions.VIEW_PORTFOLIO, portfolio=portfolio)
    assert user_can_access(view_admin, Permissions.VIEW_PORTFOLIO, portfolio=portfolio)

    # check a portfolio edit permission
    assert user_can_access(ccpo, Permissions.EDIT_PORTFOLIO_NAME, portfolio=portfolio)
    assert user_can_access(
        edit_admin, Permissions.EDIT_PORTFOLIO_NAME, portfolio=portfolio
    )
    with pytest.raises(UnauthorizedError):
        user_can_access(
            view_admin, Permissions.EDIT_PORTFOLIO_NAME, portfolio=portfolio
        )

    # check when portfolio_role is disabled
    PortfolioRoles.disable(portfolio_role=view_admin_pr)
    with pytest.raises(UnauthorizedError):
        user_can_access(
            view_admin, Permissions.EDIT_PORTFOLIO_NAME, portfolio=portfolio
        )


@pytest.fixture
def set_current_user(request_ctx):
    def _set_current_user(user):
        request_ctx.g.current_user = user

    yield _set_current_user

    request_ctx.g.current_user = None


def test_user_can_access_decorator_atat_level(set_current_user):
    ccpo = UserFactory.create_ccpo()
    rando = UserFactory.create()

    @user_can_access_decorator(Permissions.VIEW_AUDIT_LOG)
    def _access_activity_log(*args, **kwargs):
        return True

    set_current_user(ccpo)
    assert _access_activity_log()

    set_current_user(rando)
    with pytest.raises(UnauthorizedError):
        _access_activity_log()


def test_user_can_access_decorator_portfolio_level(set_current_user, request_ctx):
    ccpo = UserFactory.create_ccpo()
    edit_admin = UserFactory.create()
    view_admin = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=edit_admin)
    # factory gives view perms by default
    PortfolioRoleFactory.create(user=view_admin, portfolio=portfolio)

    request_ctx.g.portfolio = portfolio
    request_ctx.g.application = None

    @user_can_access_decorator(Permissions.EDIT_PORTFOLIO_NAME)
    def _edit_portfolio_name(*args, **kwargs):
        return True

    set_current_user(ccpo)
    assert _edit_portfolio_name(portfolio_id=portfolio.id)

    set_current_user(edit_admin)
    assert _edit_portfolio_name(portfolio_id=portfolio.id)

    set_current_user(view_admin)
    with pytest.raises(UnauthorizedError):
        _edit_portfolio_name(portfolio_id=portfolio.id)


def test_user_can_access_decorator_application_level(set_current_user, request_ctx):
    ccpo = UserFactory.create_ccpo()
    port_admin = UserFactory.create()
    app_user = UserFactory.create()
    rando = UserFactory.create()

    portfolio = PortfolioFactory.create(
        owner=port_admin, applications=[{"name": "Mos Eisley"}]
    )
    app = portfolio.applications[0]
    ApplicationRoleFactory.create(application=app, user=app_user)

    request_ctx.g.portfolio = portfolio
    request_ctx.g.application = app

    @user_can_access_decorator(Permissions.VIEW_APPLICATION)
    def _stroll_into_mos_eisley(*args, **kwargs):
        return True

    set_current_user(ccpo)
    assert _stroll_into_mos_eisley(application_id=app.id)

    set_current_user(port_admin)
    assert _stroll_into_mos_eisley(application_id=app.id)

    set_current_user(app_user)
    assert _stroll_into_mos_eisley(application_id=app.id)

    set_current_user(rando)
    with pytest.raises(UnauthorizedError):
        _stroll_into_mos_eisley(application_id=app.id)


def test_user_can_access_decorator_override(set_current_user):
    rando_calrissian = UserFactory.create()
    darth_vader = UserFactory.create()

    def _can_fly_the_millenium_falcon(u, *args, **kwargs):
        if u == rando_calrissian:
            return True
        else:
            raise UnauthorizedError(u, "is not rando")

    @user_can_access_decorator(
        Permissions.EDIT_PORTFOLIO_NAME, override=_can_fly_the_millenium_falcon
    )
    def _cloud_city(*args, **kwargs):
        return True

    set_current_user(rando_calrissian)
    assert _cloud_city()

    set_current_user(darth_vader)
    with pytest.raises(UnauthorizedError):
        assert _cloud_city()


def test_user_can_access_decorator_logs_access(
    set_current_user, monkeypatch, mock_logger
):
    user = UserFactory.create()  # this emits an 'Audit Event insert' event

    @user_can_access_decorator(Permissions.EDIT_PORTFOLIO_NAME)
    def _do_something(*args, **kwargs):
        return True

    set_current_user(user)

    monkeypatch.setattr(
        "atat.domain.authz.decorator.check_access", lambda *a, **k: True
    )
    num_msgs = len(mock_logger.messages)
    _do_something()
    assert len(mock_logger.messages) == num_msgs + 1
    assert "accessed" in mock_logger.messages[-1]
    assert "GET" in mock_logger.messages[-1]

    def _unauthorized(*a, **k):
        raise UnauthorizedError(user, "do something")

    monkeypatch.setattr("atat.domain.authz.decorator.check_access", _unauthorized)
    num_msgs = len(mock_logger.messages)
    with pytest.raises(UnauthorizedError):
        _do_something()

    assert len(mock_logger.messages) == num_msgs + 1
    assert "denied access" in mock_logger.messages[-1]
    assert "GET" in mock_logger.messages[-1]
