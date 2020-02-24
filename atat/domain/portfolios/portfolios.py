from sqlalchemy import or_
from typing import List
from uuid import UUID

from atat.database import db
from atat.domain.permission_sets import PermissionSets
from atat.domain.authz import Authorization
from atat.domain.portfolio_roles import PortfolioRoles

from atat.domain.invitations import PortfolioInvitations
from atat.models import (
    Portfolio,
    PortfolioStateMachine,
    FSMStates,
    Permissions,
    PortfolioRole,
    PortfolioRoleStatus,
    TaskOrder,
    CLIN,
)

from .query import PortfoliosQuery, PortfolioStateMachinesQuery
from .scopes import ScopedPortfolio


class PortfolioError(Exception):
    pass


class PortfolioDeletionApplicationsExistError(Exception):
    pass


class PortfolioStateMachines(object):
    @classmethod
    def create(cls, portfolio, **sm_attrs):
        sm_attrs.update({"portfolio": portfolio})
        sm = PortfolioStateMachinesQuery.create(**sm_attrs)
        return sm


class Portfolios(object):
    @classmethod
    def get_or_create_state_machine(cls, portfolio):
        """
        get or create Portfolio State Machine for a Portfolio
        """
        return portfolio.state_machine or PortfolioStateMachines.create(portfolio)

    @classmethod
    def create(cls, user, portfolio_attrs):
        portfolio = PortfoliosQuery.create(**portfolio_attrs)
        perms_sets = PermissionSets.get_many(PortfolioRoles.PORTFOLIO_PERMISSION_SETS)
        Portfolios._create_portfolio_role(
            user,
            portfolio,
            status=PortfolioRoleStatus.ACTIVE,
            permission_sets=perms_sets,
        )
        PortfoliosQuery.add_and_commit(portfolio)
        return portfolio

    @classmethod
    def get(cls, user, portfolio_id):
        portfolio = PortfoliosQuery.get(portfolio_id)
        return ScopedPortfolio(user, portfolio)

    @classmethod
    def delete(cls, portfolio):
        if len(portfolio.applications) != 0:
            raise PortfolioDeletionApplicationsExistError()

        for portfolio_role in portfolio.roles:
            PortfolioRoles.disable(portfolio_role=portfolio_role, commit=False)

        portfolio.deleted = True

        db.session.add(portfolio)
        db.session.commit()

        return portfolio

    @classmethod
    def get_for_update(cls, portfolio_id):
        portfolio = PortfoliosQuery.get(portfolio_id)

        return portfolio

    @classmethod
    def for_user(cls, user):
        if Authorization.has_atat_permission(user, Permissions.VIEW_PORTFOLIO):
            portfolios = PortfoliosQuery.get_all()
        else:
            portfolios = PortfoliosQuery.get_for_user(user)
        return portfolios

    @classmethod
    def add_member(cls, portfolio, member, permission_sets=None):
        portfolio_role = PortfolioRoles.add(member, portfolio.id, permission_sets)
        return portfolio_role

    @classmethod
    def invite(cls, portfolio, inviter, member_data):
        permission_sets = PortfolioRoles._permission_sets_for_names(
            member_data.get("permission_sets", [])
        )
        role = PortfolioRole(portfolio=portfolio, permission_sets=permission_sets)

        invitation = PortfolioInvitations.create(
            inviter=inviter, role=role, member_data=member_data["user_data"]
        )

        PortfoliosQuery.add_and_commit(role)

        return invitation

    @classmethod
    def update_member(cls, member, permission_sets):
        return PortfolioRoles.update(member, permission_sets)

    @classmethod
    def _create_portfolio_role(
        cls, user, portfolio, status=PortfolioRoleStatus.PENDING, permission_sets=None
    ):
        if permission_sets is None:
            permission_sets = []

        portfolio_role = PortfoliosQuery.create_portfolio_role(
            user, portfolio, status=status, permission_sets=permission_sets
        )
        PortfoliosQuery.add_and_commit(portfolio_role)
        return portfolio_role

    @classmethod
    def update(cls, portfolio, new_data):
        if "name" in new_data:
            portfolio.name = new_data["name"]

        if "description" in new_data:
            portfolio.description = new_data["description"]

        PortfoliosQuery.add_and_commit(portfolio)

    @classmethod
    def base_provision_query(cls):
        return db.session.query(Portfolio.id)

    @classmethod
    def get_portfolios_pending_provisioning(cls, now) -> List[UUID]:
        """
        Any portfolio with a corresponding State Machine that is either:
            not started yet,
            failed in creating a tenant
            failed
        """

        results = (
            db.session.query(Portfolio.id)
            .join(PortfolioStateMachine)
            .join(TaskOrder)
            .join(CLIN)
            .filter(Portfolio.deleted == False)
            .filter(CLIN.start_date <= now)
            .filter(CLIN.end_date > now)
            .filter(
                or_(
                    PortfolioStateMachine.state == FSMStates.UNSTARTED,
                    PortfolioStateMachine.state.like("%CREATED"),
                )
            )
        )
        return [id_ for id_, in results]
