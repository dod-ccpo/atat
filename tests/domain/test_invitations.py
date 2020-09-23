import re

import pendulum
import pytest

from atat.domain.audit_log import AuditLog
from atat.domain.invitations import (
    ExpiredError,
    InvitationError,
    NotFoundError,
    PortfolioInvitations,
    WrongUserError,
)
from atat.models import InvitationStatus
from atat.models.portfolio_role import Status as PortfolioRoleStatus
from tests.factories import (
    PortfolioFactory,
    PortfolioInvitationFactory,
    PortfolioRoleFactory,
    UserFactory,
)


def test_create_invitation():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    invite = PortfolioInvitations.create(
        portfolio.owner, role, user.to_dictionary(), commit=True
    )
    assert invite.role == role
    assert invite.inviter == portfolio.owner
    assert invite.status == InvitationStatus.PENDING
    assert re.match(r"^[\w\-_]+$", invite.token)
    assert invite.role.status == PortfolioRoleStatus.PENDING


def test_accept_invitation():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    invite = PortfolioInvitations.create(
        portfolio.owner, role, user.to_dictionary(), commit=True
    )
    assert invite.is_pending
    accepted_invite = PortfolioInvitations.accept(user, invite.token)
    assert accepted_invite.is_accepted
    assert accepted_invite.role.is_active


def test_accept_expired_invitation():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    role = PortfolioRoleFactory.create(portfolio=portfolio)
    increment = PortfolioInvitations.EXPIRATION_LIMIT_MINUTES + 1
    expiration_time = pendulum.now(tz="UTC").subtract(minutes=increment)
    invite = PortfolioInvitationFactory.create(
        expiration_time=expiration_time,
        status=InvitationStatus.PENDING,
        role=role,
        dod_id=user.dod_id,
    )
    with pytest.raises(ExpiredError):
        PortfolioInvitations.accept(user, invite.token)

    assert invite.is_rejected
    assert invite.role.status == PortfolioRoleStatus.PENDING


def test_accept_rejected_invite():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    role = PortfolioRoleFactory.create(portfolio=portfolio)
    invite = PortfolioInvitationFactory.create(
        status=InvitationStatus.REJECTED_EXPIRED, role=role, dod_id=user.dod_id
    )
    with pytest.raises(InvitationError):
        PortfolioInvitations.accept(user, invite.token)
    assert invite.role.status == PortfolioRoleStatus.PENDING


def test_accept_revoked_invite():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    role = PortfolioRoleFactory.create(portfolio=portfolio)
    invite = PortfolioInvitationFactory.create(
        status=InvitationStatus.REVOKED, role=role, dod_id=user.dod_id
    )
    with pytest.raises(InvitationError):
        PortfolioInvitations.accept(user, invite.token)
    assert invite.role.status == PortfolioRoleStatus.PENDING


def test_wrong_user_accepts_invitation():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    role = PortfolioRoleFactory.create(portfolio=portfolio)
    wrong_user = UserFactory.create()
    invite = PortfolioInvitationFactory.create(role=role, dod_id=user.dod_id)
    with pytest.raises(WrongUserError):
        PortfolioInvitations.accept(wrong_user, invite.token)
    assert invite.role.status == PortfolioRoleStatus.PENDING


def test_user_cannot_accept_invitation_accepted_by_wrong_user():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    role = PortfolioRoleFactory.create(portfolio=portfolio)
    wrong_user = UserFactory.create()
    invite = PortfolioInvitationFactory.create(role=role, dod_id=user.dod_id)
    with pytest.raises(WrongUserError):
        PortfolioInvitations.accept(wrong_user, invite.token)
    with pytest.raises(InvitationError):
        PortfolioInvitations.accept(user, invite.token)
    assert invite.role.status == PortfolioRoleStatus.PENDING


def test_accept_invitation_twice():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    role = PortfolioRoleFactory.create(portfolio=portfolio)
    invite = PortfolioInvitationFactory.create(role=role, dod_id=user.dod_id)
    PortfolioInvitations.accept(user, invite.token)
    with pytest.raises(InvitationError):
        PortfolioInvitations.accept(user, invite.token)
    assert invite.role.is_active


def test_revoke_invitation():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    invite = PortfolioInvitationFactory.create(role=role, dod_id=user.dod_id)
    assert invite.is_pending
    PortfolioInvitations.revoke(invite.token)
    assert invite.is_revoked
    assert invite.role.status == PortfolioRoleStatus.DISABLED


def test_resend_invitation(session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    role = PortfolioRoleFactory.create(portfolio=portfolio)
    first_invite = PortfolioInvitationFactory.create(role=role, dod_id=user.dod_id)
    assert first_invite.is_pending
    second_invite = PortfolioInvitations.resend(user, first_invite.token)
    assert first_invite.is_revoked
    assert second_invite.is_pending


@pytest.mark.audit_log
def test_audit_event_for_accepted_invite():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    role = PortfolioRoleFactory.create(portfolio=portfolio)
    invite = PortfolioInvitationFactory.create(role=role, dod_id=user.dod_id)
    invite = PortfolioInvitations.accept(user, invite.token)

    accepted_event = AuditLog.get_by_resource(invite.id)[0]
    assert "email" in accepted_event.event_details
    assert "dod_id" in accepted_event.event_details
