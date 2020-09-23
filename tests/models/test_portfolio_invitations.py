import pendulum

from atat.models import InvitationStatus, PortfolioRoleStatus
from tests.factories import (
    PortfolioFactory,
    PortfolioInvitationFactory,
    PortfolioRoleFactory,
    UserFactory,
)


def test_expired_invite_is_not_revokable():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        expiration_time=pendulum.now(tz="UTC").subtract(minutes=60),
        role=portfolio_role,
    )
    assert not invite.is_revokable


def test_unexpired_invite_is_revokable():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(role=portfolio_role)
    assert invite.is_revokable


def test_invite_is_not_revokable_if_invite_is_not_pending():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        role=portfolio_role, status=InvitationStatus.ACCEPTED
    )
    assert not invite.is_revokable
