from flask import Blueprint
from flask import current_app as app
from flask import redirect, render_template, request, url_for

from atat.domain.audit_log import AuditLog
from atat.domain.authz.decorator import user_can_access_decorator as user_can
from atat.domain.common import Paginator
from atat.domain.exceptions import NotFoundError
from atat.domain.portfolios import Portfolios
from atat.domain.users import Users
from atat.forms.ccpo_user import CCPOUserForm
from atat.forms.data import SERVICE_BRANCHES
from atat.models import User
from atat.models.permissions import Permissions
from atat.utils.context_processors import atat as atat_context_processor
from atat.utils.flash import formatted_flash as flash

bp = Blueprint("ccpo", __name__)
bp.context_processor(atat_context_processor)

_CCPO_USERS_ROUTE = "ccpo.users"


@bp.route("/activity-history")
@user_can(Permissions.VIEW_AUDIT_LOG, message="view activity log")
def activity_history():
    if app.config.get("USE_AUDIT_LOG", False):
        pagination_opts = Paginator.get_pagination_opts(request)
        audit_events = AuditLog.get_all_events(pagination_opts)
        return render_template("audit_log/audit_log.html", audit_events=audit_events)
    else:
        return redirect("/")


@bp.route("/ccpo-users")
@user_can(Permissions.VIEW_CCPO_USER, message="view ccpo users")
def users():
    users = Users.get_ccpo_users()
    users_info = [(user, CCPOUserForm(obj=user)) for user in users]
    return render_template("ccpo/users.html", users_info=users_info)


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


@bp.route("/ccpo-users/new")
@user_can(Permissions.CREATE_CCPO_USER, message="create ccpo user")
def add_new_user():
    form = CCPOUserForm()
    return render_template("ccpo/add_user.html", form=form)


@bp.route("/ccpo-users/new", methods=["POST"])
@user_can(Permissions.CREATE_CCPO_USER, message="create ccpo user")
def submit_new_user():
    try:
        new_user = Users.get_by_dod_id(request.form["dod_id"])
        form = CCPOUserForm(obj=new_user)
    except NotFoundError:
        flash("ccpo_user_not_found")
        return redirect(url_for(_CCPO_USERS_ROUTE))

    return render_template("ccpo/confirm_user.html", new_user=new_user, form=form)


@bp.route("/ccpo-users/confirm-new", methods=["POST"])
@user_can(Permissions.CREATE_CCPO_USER, message="create ccpo user")
def confirm_new_user():
    user = Users.get_by_dod_id(request.form["dod_id"])
    Users.give_ccpo_perms(user)
    flash("ccpo_user_added", user_name=user.full_name)
    return redirect(url_for(_CCPO_USERS_ROUTE))


@bp.route("/ccpo-users/remove-access/<user_id>", methods=["POST"])
@user_can(Permissions.DELETE_CCPO_USER, message="remove ccpo user")
def remove_access(user_id):
    user = Users.get(user_id)
    Users.revoke_ccpo_perms(user)
    flash("ccpo_user_removed", user_name=user.full_name)
    return redirect(url_for(_CCPO_USERS_ROUTE))
