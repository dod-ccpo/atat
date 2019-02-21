from atst.domain.portfolio_roles import PortfolioRoles
from atst.models.permissions import Permissions
from atst.domain.exceptions import UnauthorizedError


class Authorization(object):
    @classmethod
    def has_portfolio_permission(cls, user, portfolio, permission):
        return permission in PortfolioRoles.portfolio_role_permissions(
            portfolio, user
        ) or Authorization.is_ccpo(user)

    @classmethod
    def has_atat_permission(cls, user, permission):
        return permission in user.atat_role.permissions

    @classmethod
    def is_in_portfolio(cls, user, portfolio):
        return user in portfolio.users

    @classmethod
    def check_portfolio_permission(cls, user, portfolio, permission, message):
        if not Authorization.has_portfolio_permission(user, portfolio, permission):
            raise UnauthorizedError(user, message)

    @classmethod
    def check_atat_permission(cls, user, permission, message):
        if not Authorization.has_atat_permission(user, permission):
            raise UnauthorizedError(user, message)

    @classmethod
    def can_view_audit_log(cls, user):
        return Authorization.has_atat_permission(user, Permissions.VIEW_AUDIT_LOG)

    @classmethod
    def is_ccpo(cls, user):
        return user.atat_role.name == "ccpo"

    @classmethod
    def is_ko(cls, user, task_order):
        return user == task_order.contracting_officer

    @classmethod
    def is_cor(cls, user, task_order):
        return user == task_order.contracting_officer_representative

    @classmethod
    def is_so(cls, user, task_order):
        return user == task_order.security_officer

    @classmethod
    def check_is_ko_or_cor(cls, user, task_order):
        if Authorization.is_ko(user, task_order) or Authorization.is_cor(
            user, task_order
        ):
            return True
        else:
            raise UnauthorizedError(user, "not KO or COR")

    @classmethod
    def check_is_ko(cls, user, task_order):
        if task_order.contracting_officer != user:
            message = "review task order {}".format(task_order.id)
            raise UnauthorizedError(user, message)

    @classmethod
    def check_is_so(cls, user, task_order):
        if task_order.security_officer != user:
            message = "review task order {}".format(task_order.id)
            raise UnauthorizedError(user, message)

    @classmethod
    def check_task_order_permission(cls, user, task_order, permission, message):
        if Authorization._check_is_task_order_officer(user, task_order):
            return True

        Authorization.check_portfolio_permission(
            user, task_order.portfolio, permission, message
        )

    @classmethod
    def _check_is_task_order_officer(cls, user, task_order):
        for officer in [
            "contracting_officer",
            "contracting_officer_representative",
            "security_officer",
        ]:
            if getattr(task_order, officer, None) == user:
                return True

        return False
