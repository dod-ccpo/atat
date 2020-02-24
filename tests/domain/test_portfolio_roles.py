from atat.domain.permission_sets import PermissionSets
from atat.domain.portfolio_roles import PortfolioRoles
from atat.domain.users import Users
from atat.models.permissions import Permissions
from atat.models.portfolio_role import Status as PortfolioRoleStatus

from tests.factories import (
    PortfolioFactory,
    UserFactory,
    PortfolioInvitationFactory,
    PortfolioRoleFactory,
)


def test_add_portfolio_role_with_permission_sets():
    portfolio = PortfolioFactory.create()
    new_user = UserFactory.create()
    permission_sets = [PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT]
    port_role = PortfolioRoles.add(
        new_user, portfolio.id, permission_sets=permission_sets
    )
    assert len(port_role.permission_sets) == 6
    expected_names = [
        PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT,
        PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
        PermissionSets.VIEW_PORTFOLIO_FUNDING,
        PermissionSets.VIEW_PORTFOLIO_REPORTS,
        PermissionSets.VIEW_PORTFOLIO_ADMIN,
        PermissionSets.VIEW_PORTFOLIO,
    ]
    actual_names = [prms.name for prms in port_role.permission_sets]
    assert expected_names == expected_names


def test_disable_portfolio_role():
    portfolio_role = PortfolioRoleFactory.create(status=PortfolioRoleStatus.ACTIVE)
    assert portfolio_role.status == PortfolioRoleStatus.ACTIVE

    PortfolioRoles.disable(portfolio_role=portfolio_role)
    assert portfolio_role.status == PortfolioRoleStatus.DISABLED


def test_revoke_ppoc_permissions():
    portfolio = PortfolioFactory.create()
    portfolio_role = PortfolioRoles.get(
        portfolio_id=portfolio.id, user_id=portfolio.owner.id
    )

    assert Permissions.EDIT_PORTFOLIO_POC in portfolio_role.permissions

    PortfolioRoles.revoke_ppoc_permissions(portfolio_role=portfolio_role)
    assert Permissions.EDIT_PORTFOLIO_POC not in portfolio_role.permissions


def test_make_ppoc():
    portfolio = PortfolioFactory.create()
    original_owner = portfolio.owner
    new_owner = UserFactory.create()

    new_owner_role = PortfolioRoles.add(user=new_owner, portfolio_id=portfolio.id)

    PortfolioRoles.make_ppoc(portfolio_role=new_owner_role)

    assert portfolio.owner is new_owner
    assert Permissions.EDIT_PORTFOLIO_POC in new_owner_role.permissions
    assert (
        Permissions.EDIT_PORTFOLIO_POC
        not in PortfolioRoles.get(
            portfolio_id=portfolio.id, user_id=original_owner.id
        ).permissions
    )
