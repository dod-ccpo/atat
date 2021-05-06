from flask import Blueprint, render_template, request

from atat.domain.authz.decorator import user_can_access_decorator as user_can
from atat.domain.portfolios import Portfolios
from atat.domain.users import Users
from atat.forms.ccpo_user import CCPOUserForm
from atat.forms.data import SERVICE_BRANCHES
from atat.models import Permissions, User
from atat.utils.context_processors import atat as atat_context_processor

bp = Blueprint("admin", __name__)
bp.context_processor(atat_context_processor)


def get_portfolios_from_user(user: User = None):
    if user is None:
        return ""

    portfolios = Portfolios.for_user(user)
    return [(portfolio.displayname, portfolio.portfolio_id) for portfolio in portfolios]


def service_branch_label(service_branch: str = None):
    if service_branch is None:
        return ""

    labels = list(filter(lambda x: service_branch in x, SERVICE_BRANCHES))
    if len(labels) > 0:
        return labels[0][1]

    return ""


@bp.route("/admin/users")
@user_can(Permissions.VIEW_PORTFOLIO_ADMIN, message="view all users")
def all_users_page():
    order_by = request.args.get("order-by") or "last_name"
    all_users = Users.get_users(order_by=order_by)
    users_info = [
        (
            user,
            CCPOUserForm(obj=user),
            get_portfolios_from_user(user),
            service_branch_label(user.service_branch),
        )
        for user in all_users
    ]

    return render_template(
        "admin/users.html",
        order_by=order_by,
        users_info=users_info,
        all_users=all_users,
    )


@bp.route("/admin/users/<user_id>")
@user_can(Permissions.VIEW_PORTFOLIO_ADMIN, message="view all users")
def user_page(user_id):
    user = Users.get(user_id)
    return render_template("admin/user.html", user=user)
