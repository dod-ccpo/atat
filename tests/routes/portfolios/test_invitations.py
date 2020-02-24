import pendulum
from unittest.mock import Mock

from flask import url_for

from atat.domain.portfolios import Portfolios
from atat.models import InvitationStatus, PortfolioRoleStatus
from atat.domain.permission_sets import PermissionSets

from tests.factories import *


def test_existing_member_accepts_valid_invite(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(dod_id=user.dod_id, role=role)

    # the user does not have access to the portfolio before accepting the invite
    assert len(Portfolios.for_user(user)) == 0

    user_session(user)
    response = client.get(
        url_for("portfolios.accept_invitation", portfolio_token=invite.token)
    )

    # user is redirected to the portfolio view
    assert response.status_code == 302
    assert (
        url_for("applications.portfolio_applications", portfolio_id=invite.portfolio.id)
        in response.headers["Location"]
    )
    # the one-time use invite is no longer usable
    assert invite.is_accepted
    # the user has access to the portfolio
    assert len(Portfolios.for_user(user)) == 1


def test_new_member_accepts_valid_invite(monkeypatch, client, user_session):
    portfolio = PortfolioFactory.create()
    user_info = UserFactory.dictionary()
    role = PortfolioRoleFactory.create(portfolio=portfolio)
    invite = PortfolioInvitationFactory.create(role=role, dod_id=user_info["dod_id"])

    monkeypatch.setattr(
        "atat.domain.auth.should_redirect_to_user_profile", lambda *args: False
    )
    user_session(UserFactory.create(dod_id=user_info["dod_id"]))
    response = client.get(
        url_for("portfolios.accept_invitation", portfolio_token=invite.token)
    )

    # user is redirected to the portfolio view
    assert response.status_code == 302
    assert (
        url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
        in response.headers["Location"]
    )
    # the user has access to the portfolio
    assert role.user.dod_id == user_info["dod_id"]
    assert len(role.user.portfolio_roles) == 1


def test_member_accepts_invalid_invite(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        user=user, portfolio=portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id, role=ws_role, status=InvitationStatus.REJECTED_WRONG_USER
    )
    user_session(user)
    response = client.get(
        url_for("portfolios.accept_invitation", portfolio_token=invite.token)
    )

    assert response.status_code == 404


def test_user_who_has_not_accepted_portfolio_invite_cannot_view(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()

    # create user in portfolio with invitation
    user_session(portfolio.owner)
    response = client.post(
        url_for("portfolios.invite_member", portfolio_id=portfolio.id),
        data=user.to_dictionary(),
    )

    # user tries to view portfolio before accepting invitation
    user_session(user)
    response = client.get("/portfolios/{}/applications".format(portfolio.id))
    assert response.status_code == 404


def test_user_accepts_invite_with_wrong_dod_id(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    different_user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        user=user, portfolio=portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(user_id=user.id, role=ws_role)
    user_session(different_user)
    response = client.get(
        url_for("portfolios.accept_invitation", portfolio_token=invite.token)
    )

    assert response.status_code == 404


def test_user_accepts_expired_invite(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        user=user, portfolio=portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id,
        role=ws_role,
        status=InvitationStatus.REJECTED_EXPIRED,
        expiration_time=pendulum.now(tz="utc").subtract(seconds=1),
    )
    user_session(user)
    response = client.get(
        url_for("portfolios.accept_invitation", portfolio_token=invite.token)
    )

    assert response.status_code == 404


def test_revoke_invitation(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        user=user, portfolio=portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id,
        role=ws_role,
        status=InvitationStatus.REJECTED_EXPIRED,
        expiration_time=pendulum.now(tz="utc").subtract(seconds=1),
    )
    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "portfolios.revoke_invitation",
            portfolio_id=portfolio.id,
            portfolio_token=invite.token,
        )
    )

    assert response.status_code == 302
    assert invite.is_revoked


def test_user_can_only_revoke_invites_in_their_portfolio(client, user_session):
    portfolio = PortfolioFactory.create()
    other_portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        user=user, portfolio=other_portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id,
        role=portfolio_role,
        status=InvitationStatus.REJECTED_EXPIRED,
        expiration_time=pendulum.now(tz="utc").subtract(seconds=1),
    )
    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "portfolios.revoke_invitation",
            portfolio_id=portfolio.id,
            portfolio_token=invite.token,
        )
    )

    assert response.status_code == 404
    assert not invite.is_revoked


def test_user_can_only_resend_invites_in_their_portfolio(
    monkeypatch, client, user_session
):
    job_mock = Mock()
    monkeypatch.setattr("atat.jobs.send_mail.delay", job_mock)
    portfolio = PortfolioFactory.create()
    other_portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        user=user, portfolio=other_portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id,
        role=portfolio_role,
        status=InvitationStatus.REJECTED_EXPIRED,
        expiration_time=pendulum.now(tz="utc").subtract(seconds=1),
    )
    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "portfolios.resend_invitation",
            portfolio_id=portfolio.id,
            portfolio_token=invite.token,
        )
    )

    assert response.status_code == 404
    assert not job_mock.called


def test_resend_invitation_sends_email(monkeypatch, client, user_session):
    job_mock = Mock()
    monkeypatch.setattr("atat.jobs.send_mail.delay", job_mock)
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        user=user, portfolio=portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id, role=portfolio_role, status=InvitationStatus.PENDING
    )
    user_session(portfolio.owner)
    client.post(
        url_for(
            "portfolios.resend_invitation",
            portfolio_id=portfolio.id,
            portfolio_token=invite.token,
        ),
        data={
            "user_data-dod_id": user.dod_id,
            "user_data-first_name": user.first_name,
            "user_data-last_name": user.last_name,
            "user_data-email": user.email,
        },
    )

    assert job_mock.called


_DEFAULT_PERMS_FORM_DATA = {
    "permission_sets-perms_app_mgmt": "n",
    "permission_sets-perms_funding": "n",
    "permission_sets-perms_reporting": "n",
    "permission_sets-perms_portfolio_mgmt": "n",
}


def test_user_with_permission_has_add_member_link(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get(url_for("portfolios.admin", portfolio_id=portfolio.id))
    assert response.status_code == 200
    assert (
        url_for("portfolios.invite_member", portfolio_id=portfolio.id).encode()
        in response.data
    )


def test_invite_member(monkeypatch, client, user_session, session):
    job_mock = Mock()
    monkeypatch.setattr("atat.jobs.send_mail.delay", job_mock)
    user_data = UserFactory.dictionary()
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)

    response = client.post(
        url_for("portfolios.invite_member", portfolio_id=portfolio.id),
        data={
            "user_data-dod_id": user_data.get("dod_id"),
            "user_data-first_name": user_data.get("first_name"),
            "user_data-last_name": user_data.get("last_name"),
            "user_data-email": user_data.get("email"),
            **_DEFAULT_PERMS_FORM_DATA,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    full_name = "{} {}".format(user_data.get("first_name"), user_data.get("last_name"))
    assert full_name in response.data.decode()

    invitation = (
        session.query(PortfolioInvitation)
        .filter_by(dod_id=user_data.get("dod_id"))
        .one()
    )
    assert invitation.role.portfolio == portfolio

    assert job_mock.called
    assert len(invitation.role.permission_sets) == 5
