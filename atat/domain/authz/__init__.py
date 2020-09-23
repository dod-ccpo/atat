from atat.domain.exceptions import UnauthorizedError
from atat.models.application_role import Status as ApplicationRoleStatus
from atat.models.permissions import Permissions
from atat.models.portfolio_role import Status as PortfolioRoleStatus
from atat.utils import first_or_none


class Authorization(object):
    @classmethod
    def has_atat_permission(cls, user, permission):
        return permission in user.permissions

    @classmethod
    def has_portfolio_permission(cls, user, portfolio, permission):
        if Authorization.has_atat_permission(user, permission):
            return True

        port_role = first_or_none(
            lambda pr: pr.portfolio == portfolio, user.portfolio_roles
        )
        if port_role and port_role.status is not PortfolioRoleStatus.DISABLED:
            return permission in port_role.permissions
        else:
            return False

    @classmethod
    def has_application_permission(cls, user, application, permission):
        if Authorization.has_portfolio_permission(
            user, application.portfolio, permission
        ):
            return True

        app_role = first_or_none(
            lambda app_role: app_role.application == application, user.application_roles
        )
        if app_role and app_role.status is not ApplicationRoleStatus.DISABLED:
            return permission in app_role.permissions
        else:
            return False

    @classmethod
    def check_atat_permission(cls, user, permission, message):
        if not Authorization.has_atat_permission(user, permission):
            raise UnauthorizedError(user, message)

        return True

    @classmethod
    def check_portfolio_permission(cls, user, portfolio, permission, message):
        if not Authorization.has_portfolio_permission(user, portfolio, permission):
            raise UnauthorizedError(user, message)

        return True

    @classmethod
    def check_application_permission(cls, user, portfolio, permission, message):
        if not Authorization.has_application_permission(user, portfolio, permission):
            raise UnauthorizedError(user, message)

        return True


def user_can_access(user, permission, portfolio=None, application=None, message=None):
    if application:
        Authorization.check_application_permission(
            user, application, permission, message
        )
    elif portfolio:
        Authorization.check_portfolio_permission(user, portfolio, permission, message)
    else:
        Authorization.check_atat_permission(user, permission, message)

    return True
