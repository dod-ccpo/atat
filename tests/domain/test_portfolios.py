from uuid import uuid4

import pytest

from atat.domain.applications import Applications
from atat.domain.exceptions import NotFoundError
from atat.domain.permission_sets import PermissionSets
from atat.domain.portfolios import (
    PortfolioDeletionApplicationsExistError,
    Portfolios,
    PortfolioStateMachines,
)
from atat.models import ApplicationRoleStatus, PortfolioRoleStatus, PortfolioStates
from tests.factories import (
    ApplicationFactory,
    ApplicationRoleFactory,
    PortfolioFactory,
    PortfolioRoleFactory,
    UserFactory,
    get_all_portfolio_permission_sets,
)
from tests.utils import EnvQueryTest


@pytest.fixture(scope="function")
def portfolio_owner():
    return UserFactory.create()


@pytest.fixture(scope="function")
def portfolio(portfolio_owner):
    portfolio = PortfolioFactory.create(owner=portfolio_owner)
    return portfolio


def test_can_create_portfolio():
    portfolio = PortfolioFactory.create(name="frugal-whale")
    assert portfolio.name == "frugal-whale"


def test_get_nonexistent_portfolio_raises():
    with pytest.raises(NotFoundError):
        Portfolios.get(UserFactory.build(), uuid4())


def test_creating_portfolio_adds_owner(portfolio, portfolio_owner):
    assert portfolio.roles[0].user == portfolio_owner


def test_portfolio_has_timestamps(portfolio):
    assert portfolio.time_created == portfolio.time_updated


def test_update_portfolio_role_role(portfolio, portfolio_owner):
    PortfolioRoleFactory._meta.sqlalchemy_session_persistence = "flush"
    member = PortfolioRoleFactory.create(portfolio=portfolio)
    permission_sets = [PermissionSets.EDIT_PORTFOLIO_FUNDING]

    updated_member = Portfolios.update_member(member, permission_sets=permission_sets)
    assert updated_member.portfolio == portfolio


def test_scoped_portfolio_for_admin_missing_view_apps_perms(portfolio_owner, portfolio):
    Applications.create(
        portfolio.owner,
        portfolio,
        "My Application 2",
        "My application 2",
        ["dev", "staging", "prod"],
    )
    restricted_admin = UserFactory.create()
    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=restricted_admin,
        permission_sets=[PermissionSets.get(PermissionSets.VIEW_PORTFOLIO)],
    )
    scoped_portfolio = Portfolios.get(restricted_admin, portfolio.id)
    assert scoped_portfolio.id == portfolio.id
    assert len(portfolio.applications) == 1
    assert len(scoped_portfolio.applications) == 0


def test_scoped_portfolio_returns_all_applications_for_portfolio_admin(
    portfolio, portfolio_owner
):
    for i in range(5):
        Applications.create(
            portfolio.owner,
            portfolio,
            f"My Application {i}",
            "My application",
            ["dev", "staging", "prod"],
        )

    admin = UserFactory.create()
    perm_sets = get_all_portfolio_permission_sets()
    PortfolioRoleFactory.create(
        user=admin, portfolio=portfolio, permission_sets=perm_sets
    )
    scoped_portfolio = Portfolios.get(admin, portfolio.id)

    assert len(scoped_portfolio.applications) == 5
    assert len(scoped_portfolio.applications[0].environments) == 3


def test_scoped_portfolio_returns_all_applications_for_portfolio_owner(
    portfolio, portfolio_owner
):
    for i in range(5):
        Applications.create(
            portfolio.owner,
            portfolio,
            f"My Application {i}",
            "My application",
            ["dev", "staging", "prod"],
        )

    scoped_portfolio = Portfolios.get(portfolio_owner, portfolio.id)

    assert len(scoped_portfolio.applications) == 5
    assert len(scoped_portfolio.applications[0].environments) == 3


def test_for_user_returns_portfolios_for_applications_user_invited_to():
    bob = UserFactory.create()
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)
    ApplicationRoleFactory.create(
        application=application, user=bob, status=ApplicationRoleStatus.ACTIVE
    )

    assert portfolio in Portfolios.for_user(user=bob)


def test_for_user_returns_active_portfolios_for_user(portfolio, portfolio_owner):
    bob = UserFactory.create()
    PortfolioRoleFactory.create(
        user=bob, portfolio=portfolio, status=PortfolioRoleStatus.ACTIVE
    )
    PortfolioFactory.create()

    bobs_portfolios = Portfolios.for_user(bob)

    assert len(bobs_portfolios) == 1


def test_for_user_does_not_return_inactive_portfolios(portfolio, portfolio_owner):
    bob = UserFactory.create()
    Portfolios.add_member(portfolio, bob)
    PortfolioFactory.create()
    bobs_portfolios = Portfolios.for_user(bob)

    assert len(bobs_portfolios) == 0


def test_for_user_returns_all_portfolios_for_ccpo(portfolio, portfolio_owner):
    sam = UserFactory.create_ccpo()
    PortfolioFactory.create()

    sams_portfolios = Portfolios.for_user(sam)
    assert len(sams_portfolios) == 2


def test_can_create_portfolios_with_matching_names():
    portfolio_name = "Great Portfolio"
    PortfolioFactory.create(name=portfolio_name)
    PortfolioFactory.create(name=portfolio_name)


def test_disabled_members_dont_show_up(session):
    portfolio = PortfolioFactory.create()
    PortfolioRoleFactory.create(portfolio=portfolio, status=PortfolioRoleStatus.ACTIVE)
    PortfolioRoleFactory.create(
        portfolio=portfolio, status=PortfolioRoleStatus.DISABLED
    )

    # should only return portfolio owner and ACTIVE member
    assert len(portfolio.members) == 2


def test_does_not_count_disabled_members(session):
    portfolio = PortfolioFactory.create()
    PortfolioRoleFactory.create(portfolio=portfolio, status=PortfolioRoleStatus.ACTIVE)
    PortfolioRoleFactory.create(portfolio=portfolio)
    PortfolioRoleFactory.create(
        portfolio=portfolio, status=PortfolioRoleStatus.DISABLED
    )

    assert portfolio.user_count == 3


def test_invite():
    portfolio = PortfolioFactory.create()
    inviter = UserFactory.create()
    member_data = UserFactory.dictionary()

    invitation = Portfolios.invite(portfolio, inviter, {"user_data": member_data})

    assert invitation.role
    assert invitation.role.portfolio == portfolio
    assert invitation.role.user is None
    assert invitation.dod_id == member_data["dod_id"]


def test_delete_success():
    portfolio = PortfolioFactory.create()

    assert not portfolio.deleted

    Portfolios.delete(portfolio=portfolio)

    assert portfolio.deleted


def test_delete_failure_with_applications():
    portfolio = PortfolioFactory.create()
    ApplicationFactory.create(portfolio=portfolio)

    assert not portfolio.deleted

    with pytest.raises(PortfolioDeletionApplicationsExistError):
        Portfolios.delete(portfolio=portfolio)

    assert not portfolio.deleted


def test_for_user_does_not_include_deleted_portfolios():
    user = UserFactory.create()
    PortfolioFactory.create(owner=user, deleted=True)
    assert len(Portfolios.for_user(user)) == 0


def test_for_user_does_not_include_deleted_application_roles():
    user1 = UserFactory.create()
    user2 = UserFactory.create()
    portfolio = PortfolioFactory.create()
    app = ApplicationFactory.create(portfolio=portfolio)
    ApplicationRoleFactory.create(
        status=ApplicationRoleStatus.ACTIVE, user=user1, application=app
    )
    assert len(Portfolios.for_user(user1)) == 1
    ApplicationRoleFactory.create(
        status=ApplicationRoleStatus.ACTIVE, user=user2, application=app, deleted=True
    )
    assert len(Portfolios.for_user(user2)) == 0


def test_create_state_machine(portfolio):
    fsm = PortfolioStateMachines.create(portfolio)
    assert fsm


class TestGetPortfoliosPendingCreate(EnvQueryTest):
    def test_finds_unstarted(self):
        # Given: A portfolio is in its period of performance
        # Given: The portfolio's state machine is in its "UNSTARTED" stage
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.TOMORROW)],
            state_machine_status=PortfolioStates.UNSTARTED.name,
        )
        # When I query for portfolios pending provisioning
        portfolios_pending = Portfolios.get_portfolios_pending_provisioning(self.NOW)
        # Then the query will return the portfolio
        assert len(portfolios_pending) == 1

    def test_finds_created(self):
        # Given: A portfolio is in its period of performance
        # Given: The portfolio's state machine is in a _CREATED stage
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.TOMORROW)],
            state_machine_status=PortfolioStates.TENANT_CREATED.name,
        )
        # When I query for portfolios pending provisioning
        portfolios_pending = Portfolios.get_portfolios_pending_provisioning(self.NOW)
        # Then the query will return the portfolio
        assert len(portfolios_pending) == 1

    def test_does_not_find_failed(self):
        # Given: A portfolio is in its period of performance
        # Given: The portfolio's state machine is in a _FAILED stage
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.TOMORROW)],
            state_machine_status=PortfolioStates.TENANT_FAILED.name,
        )
        # When I query for portfolios pending provisioning
        portfolios_pending = Portfolios.get_portfolios_pending_provisioning(self.NOW)
        # Then the query will not return the portfolio
        assert len(portfolios_pending) == 0

    def test_with_future_clins_and_no_state_machine(self):
        # Given: The portfolio has not entered its period of performance
        # Given: The portfolio has not begun the provisioning process
        self.create_portfolio_with_clins([(self.TOMORROW, self.TOMORROW)])
        # When I query for portfolios pending provisioning
        portfolios_pending = Portfolios.get_portfolios_pending_provisioning(self.NOW)
        # Then the query will return 0 portfolios
        assert len(portfolios_pending) == 0

    def test_with_future_clins_and_state_machine(self):
        # Given: The portfolio has not entered a period of performance
        # Given: The portfolio has begun the provisioning process
        self.create_portfolio_with_clins(
            [(self.TOMORROW, self.TOMORROW)],
            state_machine_status=PortfolioStates.TENANT_CREATED.name,
        )
        # When I query for portfolios pending provisioning
        portfolios_pending = Portfolios.get_portfolios_pending_provisioning(self.NOW)
        # Then the query will return 0 portfolios
        assert len(portfolios_pending) == 0

    def test_with_expired_clins_and_no_state_machine(self):
        # Given: A portfolio has exited its period of performance
        # Given: The portfolio has not started the provisioning process
        self.create_portfolio_with_clins([(self.YESTERDAY, self.YESTERDAY)])
        # When I query for portfolios pending provisioning
        portfolios_pending = Portfolios.get_portfolios_pending_provisioning(self.NOW)
        # Then the query will return 0 portfolios
        assert len(portfolios_pending) == 0

    def test_with_expired_clins_and_state_machine(self):
        # Given: A portfolio has exited its period of performance
        # Given: The portfolio is in the middle of the provisioning process
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.YESTERDAY)],
            state_machine_status=PortfolioStates.TENANT_CREATED.name,
        )
        # When I query for portfolios pending provisioning
        portfolios_pending = Portfolios.get_portfolios_pending_provisioning(self.NOW)
        # Then the query will return 0 portfolios
        assert len(portfolios_pending) == 0

    def test_with_active_clins_and_no_state_machine(self):
        # Given: A portfolio is in its period of performance
        # Given: The portfolio has begun the provisioning process
        self.create_portfolio_with_clins([(self.YESTERDAY, self.TOMORROW)])
        # When I query for portfolios pending provisioning
        pending_portfolios = Portfolios.get_portfolios_pending_provisioning(self.NOW)
        # Then the query will return the pending portfolio
        assert len(pending_portfolios) == 1

    def test_with_active_clins_and_state_machine(self):
        # Given: A portfolio is in its period of performance
        # Given: The portfolio has begun the provisioning process
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.TOMORROW)],
            state_machine_status=PortfolioStates.TENANT_CREATED.name,
        )
        # When I query for portfolios pending provisioning
        portfolios_pending = Portfolios.get_portfolios_pending_provisioning(self.NOW)
        # Then the query will return the pending portfolio
        assert len(portfolios_pending) == 1

    def test_with_unsigned_task_order(self):
        # Given: A portfolio is in its period of performance
        # Given: The portfolio has begun the provisioning process
        # Given: Portfolio is associated with an unsigned task order
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.TOMORROW)],
            state_machine_status=PortfolioStates.UNSTARTED.name,
            task_order_signed_at=None,
        )
        # When I query for portfolios pending provisioning
        portfolios_pending = Portfolios.get_portfolios_pending_provisioning(self.NOW)
        # Then the query will NOT return the pending portfolio
        assert len(portfolios_pending) == 0
