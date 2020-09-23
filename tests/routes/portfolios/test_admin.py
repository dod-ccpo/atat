from unittest.mock import MagicMock

import pytest
from flask import url_for

from atat.domain.permission_sets import PermissionSets
from atat.domain.portfolio_roles import PortfolioRoles
from atat.domain.portfolios import Portfolios
from atat.models.permissions import Permissions
from atat.models.portfolio_role import Status as PortfolioRoleStatus
from atat.utils.localization import translate
from tests.factories import PortfolioFactory, PortfolioRoleFactory, UserFactory


def test_update_portfolio_name_and_description(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.post(
        url_for("portfolios.edit", portfolio_id=portfolio.id),
        data={"name": "a cool new name", "description": "a portfolio for things"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert portfolio.name == "a cool new name"
    assert portfolio.description == "a portfolio for things"


@pytest.mark.skip(reason="Out of scope for MVP")
def updating_ppoc_successfully(client, old_ppoc, new_ppoc, portfolio):
    response = client.post(
        url_for("portfolios.update_ppoc", portfolio_id=portfolio.id, _external=True),
        data={"role_id": new_ppoc.id},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"] == url_for(
        "portfolios.admin",
        portfolio_id=portfolio.id,
        fragment="primary-point-of-contact",
        _anchor="primary-point-of-contact",
        _external=True,
    )
    assert portfolio.owner_role.id == new_ppoc.id
    assert Permissions.EDIT_PORTFOLIO_POC in new_ppoc.permissions
    assert Permissions.EDIT_PORTFOLIO_POC not in old_ppoc.permissions


@pytest.mark.skip(reason="Out of scope for MVP")
def test_update_ppoc_no_user_id_specified(client, user_session):
    portfolio = PortfolioFactory.create()

    user_session(portfolio.owner)

    response = client.post(
        url_for("portfolios.update_ppoc", portfolio_id=portfolio.id, _external=True),
        follow_redirects=False,
    )

    assert response.status_code == 404


@pytest.mark.skip(reason="Out of scope for MVP")
def test_update_ppoc_to_member_not_on_portfolio(client, user_session):
    portfolio = PortfolioFactory.create()
    original_ppoc = portfolio.owner
    non_portfolio_member = UserFactory.create()

    user_session(original_ppoc)

    response = client.post(
        url_for("portfolios.update_ppoc", portfolio_id=portfolio.id, _external=True),
        data={"user_id": non_portfolio_member.id},
        follow_redirects=False,
    )

    assert response.status_code == 404
    assert portfolio.owner.id == original_ppoc.id


@pytest.mark.skip(reason="Out of scope for MVP")
def test_update_ppoc_when_ppoc(client, user_session):
    portfolio = PortfolioFactory.create()
    original_ppoc = portfolio.owner_role
    new_ppoc = Portfolios.add_member(
        member=UserFactory.create(),
        portfolio=portfolio,
        permission_sets=[PermissionSets.VIEW_PORTFOLIO],
    )

    user_session(original_ppoc.user)

    updating_ppoc_successfully(
        client=client, new_ppoc=new_ppoc, old_ppoc=original_ppoc, portfolio=portfolio
    )


@pytest.mark.skip(reason="Out of scope for MVP")
def test_update_ppoc_when_ccpo(client, user_session):
    ccpo = UserFactory.create_ccpo()
    portfolio = PortfolioFactory.create()
    original_ppoc = portfolio.owner_role
    new_ppoc = Portfolios.add_member(
        member=UserFactory.create(),
        portfolio=portfolio,
        permission_sets=[PermissionSets.VIEW_PORTFOLIO],
    )

    user_session(ccpo)

    updating_ppoc_successfully(
        client=client, new_ppoc=new_ppoc, old_ppoc=original_ppoc, portfolio=portfolio
    )


@pytest.mark.skip(reason="Out of scope for MVP")
def test_update_ppoc_when_not_ppoc(client, user_session):
    portfolio = PortfolioFactory.create()
    new_owner = UserFactory.create()

    user_session(new_owner)

    response = client.post(
        url_for("portfolios.update_ppoc", portfolio_id=portfolio.id, _external=True),
        data={"dod_id": new_owner.dod_id},
        follow_redirects=False,
    )

    assert response.status_code == 404


def test_portfolio_admin_screen_when_not_ppoc(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    permission_sets = PermissionSets.get_many(
        [PermissionSets.EDIT_PORTFOLIO_ADMIN, PermissionSets.VIEW_PORTFOLIO_ADMIN]
    )
    PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, permission_sets=permission_sets
    )
    user_session(user)
    response = client.get(url_for("portfolios.admin", portfolio_id=portfolio.id))
    assert response.status_code == 200
    assert portfolio.name in response.data.decode()
    assert translate("fragments.ppoc.update_btn").encode("utf8") not in response.data


def test_remove_portfolio_member(client, user_session):
    portfolio = PortfolioFactory.create()

    user = UserFactory.create()
    member = PortfolioRoleFactory.create(portfolio=portfolio, user=user)

    user_session(portfolio.owner)

    response = client.post(
        url_for(
            "portfolios.remove_member",
            portfolio_id=portfolio.id,
            portfolio_role_id=member.id,
        ),
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"] == url_for(
        "portfolios.admin",
        portfolio_id=portfolio.id,
        _anchor="portfolio-members",
        fragment="portfolio-members",
        _external=True,
    )
    assert (
        PortfolioRoles.get(portfolio_id=portfolio.id, user_id=user.id).status
        == PortfolioRoleStatus.DISABLED
    )


def test_remove_portfolio_member_self(client, user_session):
    portfolio = PortfolioFactory.create()
    portfolio_role = PortfolioRoles.get(
        portfolio_id=portfolio.id, user_id=portfolio.owner.id
    )

    user_session(portfolio.owner)

    response = client.post(
        url_for(
            "portfolios.remove_member",
            portfolio_id=portfolio.id,
            portfolio_role_id=portfolio_role.id,
        ),
        follow_redirects=False,
    )

    assert response.status_code == 404
    assert (
        PortfolioRoles.get(portfolio_id=portfolio.id, user_id=portfolio.owner.id).status
        == PortfolioRoleStatus.ACTIVE
    )


def test_remove_portfolio_member_ppoc(client, user_session):
    portfolio = PortfolioFactory.create()

    user = UserFactory.create()
    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=user,
        permission_sets=[PermissionSets.get(PermissionSets.EDIT_PORTFOLIO_ADMIN)],
    )
    ppoc_port_role = PortfolioRoles.get(
        portfolio_id=portfolio.id, user_id=portfolio.owner.id
    )

    user_session(user)

    response = client.post(
        url_for(
            "portfolios.remove_member",
            portfolio_id=portfolio.id,
            portfolio_role_id=ppoc_port_role.id,
        ),
        follow_redirects=False,
    )

    assert response.status_code == 404
    assert (
        PortfolioRoles.get(portfolio_id=portfolio.id, user_id=portfolio.owner.id).status
        == PortfolioRoleStatus.ACTIVE
    )


def test_portfolios_update_member(client, user_session):
    portfolio = PortfolioFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio,
        permission_sets=[PermissionSets.get(PermissionSets.EDIT_PORTFOLIO_ADMIN)],
    )

    form_data = {
        "perms_app_mgmt": "y",
    }

    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "portfolios.update_member",
            portfolio_id=portfolio.id,
            portfolio_role_id=portfolio_role.id,
        ),
        data=form_data,
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert portfolio_role.has_permission_set(
        PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT
    )
    assert not portfolio_role.has_permission_set(PermissionSets.EDIT_PORTFOLIO_ADMIN)


def test_can_not_update_ppoc_permissions(client, user_session):
    portfolio = PortfolioFactory.create()
    owner = portfolio.owner

    form_data = {
        "perms_app_mgmt": "y",
    }

    user_session(owner)
    response = client.post(
        url_for(
            "portfolios.update_member",
            portfolio_id=portfolio.id,
            portfolio_role_id=portfolio.owner_role.id,
        ),
        data=form_data,
        follow_redirects=False,
    )

    assert response.status_code == 400
