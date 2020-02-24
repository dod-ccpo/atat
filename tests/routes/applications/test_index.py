from flask import url_for, get_flashed_messages

from tests.factories import *

from atat.domain.applications import Applications
from atat.domain.portfolios import Portfolios
from atat.models.portfolio_role import Status as PortfolioRoleStatus

from tests.utils import captured_templates


def test_user_with_permission_has_budget_report_link(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get(
        url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
    )
    assert (
        url_for("portfolios.reports", portfolio_id=portfolio.id)
        in response.data.decode()
    )


def test_user_without_permission_has_no_budget_report_link(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    Portfolios._create_portfolio_role(
        user, portfolio, status=PortfolioRoleStatus.ACTIVE
    )
    user_session(user)
    response = client.get(
        url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
    )
    assert (
        url_for("portfolios.reports", portfolio_id=portfolio.id)
        not in response.data.decode()
    )


def test_user_with_permission_has_add_application_link(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get(
        url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
    )
    assert (
        url_for("applications.create_new_application_step_1", portfolio_id=portfolio.id)
        in response.data.decode()
    )


def test_user_without_permission_has_no_add_application_link(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    Portfolios._create_portfolio_role(user, portfolio)
    user_session(user)
    response = client.get(
        url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
    )
    assert (
        url_for("applications.create_new_application_step_1", portfolio_id=portfolio.id)
        not in response.data.decode()
    )


def test_portfolio_applications_user_with_application_roles(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()

    app1 = ApplicationFactory.create(portfolio=portfolio, name="X-Wing")
    app2 = ApplicationFactory.create(portfolio=portfolio, name="TIE Fighter")
    app3 = ApplicationFactory.create(portfolio=portfolio, name="Millenium Falcon")

    ApplicationRoleFactory.create(
        application=app1, user=user, status=ApplicationRoleStatus.ACTIVE
    )
    ApplicationRoleFactory.create(
        application=app2, user=user, status=ApplicationRoleStatus.ACTIVE
    )

    user_session(user)
    response = client.get(
        url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
    )
    assert response.status_code == 200

    body = response.data.decode()

    assert app1.name in body
    assert app2.name in body
    assert app3.name not in body
