from flask import g, render_template

from atat.domain.authz.decorator import user_can_access_decorator as user_can
from atat.domain.environment_roles import EnvironmentRoles
from atat.models.permissions import Permissions

from .blueprint import applications_bp


def has_portfolio_applications(_user, portfolio=None, **_kwargs):
    """
    If the portfolio exists and the user has access to applications
    within the scoped portfolio, the user has access to the
    portfolio landing page.
    """
    if portfolio and portfolio.applications:
        return True


@applications_bp.route("/portfolios/<portfolio_id>")
@applications_bp.route("/portfolios/<portfolio_id>/applications")
@user_can(
    Permissions.VIEW_APPLICATION,
    override=has_portfolio_applications,
    message="view portfolio applications",
)
def portfolio_applications(portfolio_id):
    user_env_roles = EnvironmentRoles.for_user(g.current_user.id, portfolio_id)
    environment_access = {
        env_role.environment_id: env_role.role.value for env_role in user_env_roles
    }

    return render_template(
        "applications/index.html", environment_access=environment_access
    )
