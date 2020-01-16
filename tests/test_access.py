from unittest.mock import Mock

import pytest
import random

from flask import url_for, Response

import atst
from atst.app import make_app, make_config
from atst.domain.auth import UNPROTECTED_ROUTES as _NO_LOGIN_REQUIRED
from atst.domain.permission_sets import PermissionSets
from atst.models import CSPRole, PortfolioRoleStatus, ApplicationRoleStatus

from tests.factories import *


from atst.app import make_config, make_app

_NO_ACCESS_CHECK_REQUIRED = _NO_LOGIN_REQUIRED + [
    "applications.accept_invitation",  # available to all users; access control is built into invitation logic
    "atst.catch_all",  # available to all users
    "atst.csp_environment_access",  # internal redirect
    "atst.home",  # available to all users
    "atst.jedi_csp_calculator",  # internal redirect
    "dev.messages",  # dev tool
    "dev.test_email",  # dev tool
    "portfolios.accept_invitation",  # available to all users; access control is built into invitation logic
    "portfolios.create_portfolio",  # create a portfolio
    "portfolios.new_portfolio_step_1",  # all users can create a portfolio
    "task_orders.get_started",  # all users can start a new TO
    "users.update_user",  # available to all users
    "users.user",  # available to all users
]


def protected_routes(app):
    _protected_routes = []

    for rule in app.url_map.iter_rules():
        args = [1] * len(rule.arguments)
        mock_args = dict(zip(rule.arguments, args))
        _n, route = rule.build(mock_args)
        if rule.endpoint in _NO_ACCESS_CHECK_REQUIRED or "/static" in route:
            continue

        _protected_routes.append((rule, route))

    return _protected_routes


sample_config = make_config({"CRL_STORAGE_PROVIDER": "LOCAL"})
sample_app = make_app(sample_config)
_PROTECTED_ROUTES = protected_routes(sample_app)


@pytest.mark.access_check
@pytest.mark.parametrize("rule,route", _PROTECTED_ROUTES)
def test_all_protected_routes_have_access_control(
    rule, route, mocker, client, user_session, monkeypatch
):
    """
    This tests that all routes, except the ones in
    _NO_ACCESS_CHECK_REQUIRED, are protected by the access
    decorator.
    """
    # monkeypatch any object lookups that might happen in the access decorator
    monkeypatch.setattr("atst.domain.portfolios.Portfolios.for_user", lambda *a: [])
    monkeypatch.setattr("atst.domain.portfolios.Portfolios.get", lambda *a: None)
    monkeypatch.setattr("atst.domain.task_orders.TaskOrders.get", lambda *a: Mock())
    monkeypatch.setattr("atst.domain.applications.Applications.get", lambda *a: Mock())
    monkeypatch.setattr(
        "atst.domain.invitations.PortfolioInvitations._get", lambda *a: Mock()
    )
    monkeypatch.setattr("atst.app.assign_resources", lambda *a: None)

    # monkeypatch the error handler
    monkeypatch.setattr(
        "atst.routes.errors.handle_error", lambda *a, **k: ("error", 500)
    )

    # patch the internal function the access decorator uses so that
    # we can check that it was called
    mocker.patch("atst.domain.authz.decorator.check_access")

    user = UserFactory.create()
    user_session(user)

    method = "get" if "GET" in rule.methods else "post"
    getattr(client, method)(route)

    assert (
        atst.domain.authz.decorator.check_access.call_count == 1
    ), "no access control for {}".format(rule.endpoint)


def user_with(*perm_sets_names):
    return UserFactory.create(permission_sets=PermissionSets.get_many(perm_sets_names))


@pytest.fixture(scope="session")
def app(request):
    config = make_config(direct_config={"DEBUG": False})
    _app = make_app(config)

    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope="session")
def client(app):
    yield app.test_client()


@pytest.fixture
def get_url_assert_status(no_debug_client, user_session):
    def _get_url_assert_status(user, url, status):
        user_session(user)
        resp = no_debug_client.get(url)
        assert resp.status_code == status

    return _get_url_assert_status


@pytest.fixture
def post_url_assert_status(no_debug_client, user_session):
    def _get_url_assert_status(user, url, status, data=None):
        user_session(user)
        resp = no_debug_client.post(url, data=data)
        assert resp.status_code == status

    return _get_url_assert_status


# ccpo.activity_history
@pytest.mark.audit_log
def test_atst_activity_history_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_AUDIT_LOG)
    rando = user_with()

    url = url_for("ccpo.activity_history")
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)


# ccpo.users
def test_ccpo_users_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.MANAGE_CCPO_USERS)
    rando = user_with()

    url = url_for("ccpo.users")
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)


# ccpo.add_new_user
def test_ccpo_add_new_user_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.MANAGE_CCPO_USERS)
    rando = user_with()

    url = url_for("ccpo.add_new_user")
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)


# ccpo.submit_new_user
def test_ccpo_submit_new_user_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.MANAGE_CCPO_USERS)
    rando = user_with()

    url = url_for("ccpo.submit_new_user")
    post_url_assert_status(ccpo, url, 302, data={"dod_id": "1234567890"})
    post_url_assert_status(rando, url, 404, data={"dod_id": "1234567890"})


# ccpo.confirm_new_user
def test_ccpo_confirm_new_user_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.MANAGE_CCPO_USERS)
    rando = user_with()
    user = UserFactory.create()

    url = url_for("ccpo.confirm_new_user")
    post_url_assert_status(ccpo, url, 302, data={"dod_id": user.dod_id})
    post_url_assert_status(rando, url, 404, data={"dod_id": user.dod_id})


# ccpo.remove_access
def test_ccpo_remove_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.MANAGE_CCPO_USERS)
    rando = user_with()
    user = UserFactory.create_ccpo()

    url = url_for("ccpo.remove_access", user_id=user.id)
    post_url_assert_status(rando, url, 404)
    post_url_assert_status(ccpo, url, 302)


# applications.access_environment
def test_applications_access_environment_access(get_url_assert_status):
    dev = UserFactory.create()
    rando = UserFactory.create()
    ccpo = UserFactory.create_ccpo()

    portfolio = PortfolioFactory.create(
        owner=dev,
        applications=[
            {
                "name": "Mos Eisley",
                "description": "Where Han shot first",
                "environments": [
                    {
                        "name": "thebar",
                        "members": [{"user": dev, "role_name": "ADMIN"}],
                    }
                ],
            }
        ],
    )
    env = portfolio.applications[0].environments[0]

    url = url_for("applications.access_environment", environment_id=env.id)
    get_url_assert_status(dev, url, 302)
    get_url_assert_status(rando, url, 404)
    get_url_assert_status(ccpo, url, 404)


# applications.view_new_application_step_1
def test_applications_get_application_step_1(get_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("applications.view_new_application_step_1", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# applications.view_new_application_step_1
def test_applications_get_application_step_1_update(get_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    application = ApplicationFactory.create(portfolio=portfolio)

    url = url_for(
        "applications.view_new_application_step_1",
        portfolio_id=portfolio.id,
        application_id=application.id,
    )
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# applications.create_or_update_new_application_step_1
def test_applications_post_application_step_1(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    application = ApplicationFactory.create(portfolio=portfolio)

    def _form_data():
        return {
            "name": "Test Application %s" % (random.randrange(1, 1000)),
            "description": "This is only a test",
        }

    url = url_for(
        "applications.create_new_application_step_1", portfolio_id=portfolio.id
    )
    post_url_assert_status(ccpo, url, 302, data=_form_data())
    post_url_assert_status(owner, url, 302, data=_form_data())
    post_url_assert_status(rando, url, 404, data=_form_data())

    url = url_for(
        "applications.update_new_application_step_1",
        portfolio_id=portfolio.id,
        application_id=application.id,
    )
    post_url_assert_status(ccpo, url, 302, data=_form_data())
    post_url_assert_status(owner, url, 302, data=_form_data())
    post_url_assert_status(rando, url, 404, data=_form_data())


# applications.view_new_application_step_2
def test_applications_get_application_step_2(get_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    application = ApplicationFactory.create(portfolio=portfolio)

    url = url_for(
        "applications.view_new_application_step_2",
        portfolio_id=portfolio.id,
        application_id=application.id,
    )
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# applications.update_new_application_step_2
def test_applications_post_application_step_2(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    application = ApplicationFactory.create(portfolio=portfolio)
    step_2_form_data = {
        "environment_names-0": "development",
        "environment_names-1": "staging",
        "environment_names-2": "production",
    }

    url = url_for(
        "applications.update_new_application_step_1",
        portfolio_id=portfolio.id,
        application_id=application.id,
    )
    post_url_assert_status(ccpo, url, 302, data=step_2_form_data)
    post_url_assert_status(owner, url, 302, data=step_2_form_data)
    post_url_assert_status(rando, url, 404, data=step_2_form_data)


# portfolios.invite_member
def test_portfolios_invite_member_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.invite_member", portfolio_id=portfolio.id)
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(owner, url, 302)
    post_url_assert_status(rando, url, 404)


# applications.settings
def test_application_settings_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(
        owner=owner,
        applications=[{"name": "Mos Eisley", "description": "Where Han shot first"}],
    )
    app = portfolio.applications[0]

    url = url_for("applications.settings", application_id=app.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.edit
def test_portfolios_edit_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.edit", portfolio_id=portfolio.id)
    post_url_assert_status(ccpo, url, 200)
    post_url_assert_status(owner, url, 200)
    post_url_assert_status(rando, url, 404)


# applications.new
def test_applications_new_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for(
        "applications.create_new_application_step_1", portfolio_id=portfolio.id
    )
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.admin
def test_portfolios_admin_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.admin", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# applications.portfolio_applications
def test_applications_portfolio_applications_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    app_user = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    application = ApplicationFactory.create(portfolio=portfolio)
    ApplicationRoleFactory.create(
        application=application, user=app_user, status=ApplicationRoleStatus.ACTIVE
    )

    url = url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(app_user, url, 200)
    get_url_assert_status(rando, url, 404)


# task_orders.portfolio_funding
def test_task_orders_portfolio_funding_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("task_orders.portfolio_funding", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.reports
def test_portfolios_portfolio_reports_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_REPORTS)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.reports", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.resend_invitation
def test_portfolios_resend_invitation_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    invitee = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    prr = PortfolioRoleFactory.create(user=invitee, portfolio=portfolio)
    invite = PortfolioInvitationFactory.create(
        user=UserFactory.create(), role=prr, inviter_id=owner.id
    )

    url = url_for(
        "portfolios.resend_invitation",
        portfolio_id=portfolio.id,
        portfolio_token=invite.token,
    )
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(owner, url, 302)
    post_url_assert_status(invitee, url, 404)
    post_url_assert_status(rando, url, 404)


# portfolios.revoke_invitation
def test_portfolios_revoke_invitation_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()

    portfolio = PortfolioFactory.create(owner=owner)

    for user, status in [(ccpo, 302), (owner, 302), (rando, 404)]:
        prt_member = user_with()
        prr = PortfolioRoleFactory.create(
            user=prt_member, portfolio=portfolio, status=PortfolioRoleStatus.ACTIVE
        )
        invite = PortfolioInvitationFactory.create(user=prt_member, role=prr)
        url = url_for(
            "portfolios.revoke_invitation",
            portfolio_id=portfolio.id,
            portfolio_token=invite.token,
        )
        post_url_assert_status(user, url, status)


# applications.update
def test_applications_update_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    dev = UserFactory.create()
    rando = UserFactory.create()

    portfolio = PortfolioFactory.create(
        owner=dev,
        applications=[{"name": "Mos Eisley", "description": "Where Han shot first"}],
    )
    app = portfolio.applications[0]

    def _form_data():
        return {
            "name": "Test Application %s" % (random.randrange(1, 1000)),
            "description": "This is only a test",
        }

    url = url_for("applications.update", application_id=app.id)
    post_url_assert_status(dev, url, 302, data=_form_data())
    post_url_assert_status(ccpo, url, 302, data=_form_data())
    post_url_assert_status(rando, url, 404, data=_form_data())


# applications.update_environments
def test_applications_update_environments(post_url_assert_status):
    ccpo = UserFactory.create_ccpo()
    dev = UserFactory.create()
    rando = UserFactory.create()

    portfolio = PortfolioFactory.create(
        owner=dev,
        applications=[{"name": "Mos Eisley", "description": "Where Han shot first"}],
    )
    app = portfolio.applications[0]
    environment = EnvironmentFactory.create(application=app)

    url = url_for("applications.update_environment", environment_id=environment.id)
    post_url_assert_status(dev, url, 302)
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(rando, url, 404)


# applications.update_member
def test_applications_update_member(post_url_assert_status):
    ccpo = UserFactory.create_ccpo()
    rando = UserFactory.create()

    application_role = ApplicationRoleFactory.create()
    application = application_role.application

    url = url_for(
        "applications.update_member",
        application_id=application.id,
        application_role_id=application_role.id,
    )
    post_url_assert_status(application.portfolio.owner, url, 302)
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(rando, url, 404)


# applications.revoke_invite
def test_applications_revoke_invite(post_url_assert_status):
    ccpo = UserFactory.create_ccpo()
    rando = UserFactory.create()
    application = ApplicationFactory.create()

    for user, status in [(ccpo, 302), (application.portfolio.owner, 302), (rando, 404)]:
        app_role = ApplicationRoleFactory.create()
        invite = ApplicationInvitationFactory.create(role=app_role)

        url = url_for(
            "applications.revoke_invite",
            application_id=application.id,
            application_role_id=app_role.id,
        )
        post_url_assert_status(user, url, status)


# applications.resend_invite
def test_applications_resend_invite(post_url_assert_status):
    ccpo = UserFactory.create_ccpo()
    rando = UserFactory.create()
    application = ApplicationFactory.create()

    for user, status in [(ccpo, 302), (application.portfolio.owner, 302), (rando, 404)]:
        app_role = ApplicationRoleFactory.create()
        invite = ApplicationInvitationFactory.create(role=app_role)

        url = url_for(
            "applications.resend_invite",
            application_id=application.id,
            application_role_id=app_role.id,
        )
        post_url_assert_status(user, url, status)


# task_orders.download_task_order_pdf
def test_task_orders_download_task_order_pdf_access(get_url_assert_status, monkeypatch):
    monkeypatch.setattr(
        "atst.routes.task_orders.downloads.send_file", lambda a: Response("")
    )
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    url = url_for("task_orders.download_task_order_pdf", task_order_id=task_order.id)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)


# task_orders.form_step_one_add_pdf
# task_orders.form_step_two_add_number
# task_orders.form_step_three_add_clins
# task_orders.form_step_four_review
# task_orders.form_step_five_confirm_signature
def test_task_orders_new_get_routes(get_url_assert_status):
    get_routes = [
        "task_orders.form_step_one_add_pdf",
        "task_orders.form_step_two_add_number",
        "task_orders.form_step_three_add_clins",
        "task_orders.form_step_four_review",
        "task_orders.form_step_five_confirm_signature",
    ]

    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(
        portfolio=portfolio,
        create_clins=[{"number": "1234567890123456789012345678901234567890123"}],
    )

    for route in get_routes:
        url = url_for(route, task_order_id=task_order.id)

        get_url_assert_status(ccpo, url, 200)
        get_url_assert_status(owner, url, 200)
        get_url_assert_status(rando, url, 404)


# task_orders.submit_form_step_one_add_pdf
# task_orders.submit_form_step_two_add_number
# task_orders.submit_form_step_three_add_clins
def test_task_orders_new_post_routes(post_url_assert_status):
    post_routes = [
        ("task_orders.submit_form_step_one_add_pdf", {"pdf": ""}),
        ("task_orders.submit_form_step_two_add_number", {"number": "1234567890"}),
        (
            "task_orders.submit_form_step_three_add_clins",
            {
                "clins-0-jedi_clin_type": "JEDI_CLIN_1",
                "clins-0-clin_number": "12312",
                "clins-0-start_date": "01/01/2020",
                "clins-0-end_date": "01/01/2021",
                "clins-0-obligated_amount": "5000",
                "clins-0-total_amount": "10000",
            },
        ),
    ]

    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    for route, data in post_routes:
        url = url_for(route, task_order_id=task_order.id)
        post_url_assert_status(owner, url, 302, data=data)
        post_url_assert_status(ccpo, url, 302, data=data)
        post_url_assert_status(rando, url, 404, data=data)
