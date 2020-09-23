from sqlalchemy.orm.exc import NoResultFound

from atat.database import db
from atat.models.portfolio_role import PortfolioRole
from atat.models.portfolio_role import Status as PortfolioRoleStatus
from atat.models.user import User

from .exceptions import NotFoundError
from .permission_sets import PermissionSets


class PortfolioRoles(object):
    @classmethod
    def get(cls, portfolio_id, user_id):
        try:
            portfolio_role = (
                db.session.query(PortfolioRole)
                .join(User)
                .filter(User.id == user_id, PortfolioRole.portfolio_id == portfolio_id)
                .one()
            )
        except NoResultFound:
            raise NotFoundError("portfolio_role")

        return portfolio_role

    @classmethod
    def get_by_id(cls, id_):
        try:
            return db.session.query(PortfolioRole).filter(PortfolioRole.id == id_).one()
        except NoResultFound:
            raise NotFoundError("portfolio_role")

    @classmethod
    def add(cls, user, portfolio_id, permission_sets=None):
        new_portfolio_role = None
        try:
            existing_portfolio_role = (
                db.session.query(PortfolioRole)
                .filter(
                    PortfolioRole.user == user,
                    PortfolioRole.portfolio_id == portfolio_id,
                )
                .one()
            )
            new_portfolio_role = existing_portfolio_role
        except NoResultFound:
            new_portfolio_role = PortfolioRole(
                user=user, portfolio_id=portfolio_id, status=PortfolioRoleStatus.PENDING
            )

        if permission_sets:
            new_portfolio_role.permission_sets = PortfolioRoles._permission_sets_for_names(
                permission_sets
            )

        user.portfolio_roles.append(new_portfolio_role)
        db.session.add(user)
        db.session.commit()

        return new_portfolio_role

    DEFAULT_PORTFOLIO_PERMISSION_SETS = {
        PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
        PermissionSets.VIEW_PORTFOLIO_FUNDING,
        PermissionSets.VIEW_PORTFOLIO_REPORTS,
        PermissionSets.VIEW_PORTFOLIO_ADMIN,
        PermissionSets.VIEW_PORTFOLIO,
    }

    PORTFOLIO_PERMISSION_SETS = DEFAULT_PORTFOLIO_PERMISSION_SETS.union(
        {
            PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT,
            PermissionSets.EDIT_PORTFOLIO_FUNDING,
            PermissionSets.EDIT_PORTFOLIO_REPORTS,
            PermissionSets.EDIT_PORTFOLIO_ADMIN,
            PermissionSets.PORTFOLIO_POC,
        }
    )

    @classmethod
    def _permission_sets_for_names(cls, set_names):
        perms_set_names = PortfolioRoles.DEFAULT_PORTFOLIO_PERMISSION_SETS.union(
            set(set_names)
        )
        return PermissionSets.get_many(perms_set_names)

    @classmethod
    def make_ppoc(cls, portfolio_role):
        portfolio = portfolio_role.portfolio
        original_owner_role = PortfolioRoles.get(
            portfolio_id=portfolio.id, user_id=portfolio.owner.id
        )
        PortfolioRoles.revoke_ppoc_permissions(portfolio_role=original_owner_role)
        PortfolioRoles.add(
            user=portfolio_role.user,
            portfolio_id=portfolio.id,
            permission_sets=PortfolioRoles.PORTFOLIO_PERMISSION_SETS,
        )

    @classmethod
    def revoke_ppoc_permissions(cls, portfolio_role):
        permission_sets = [
            permission_set.name
            for permission_set in portfolio_role.permission_sets
            if permission_set.name != PermissionSets.PORTFOLIO_POC
        ]
        PortfolioRoles.update(portfolio_role=portfolio_role, set_names=permission_sets)

    @classmethod
    def disable(cls, portfolio_role, commit=True):
        portfolio_role.status = PortfolioRoleStatus.DISABLED

        db.session.add(portfolio_role)

        if commit:
            db.session.commit()

        return portfolio_role

    @classmethod
    def update(cls, portfolio_role, set_names):
        new_permission_sets = PortfolioRoles._permission_sets_for_names(set_names)
        portfolio_role.permission_sets = new_permission_sets

        db.session.add(portfolio_role)
        db.session.commit()

        return portfolio_role

    @classmethod
    def enable(cls, portfolio_role, user):
        portfolio_role.status = PortfolioRoleStatus.ACTIVE
        portfolio_role.user = user

        db.session.add(portfolio_role)
        db.session.commit()
