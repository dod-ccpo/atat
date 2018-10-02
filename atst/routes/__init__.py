import urllib.parse as url
from flask import Blueprint, render_template, g, redirect, session, url_for, request

from flask import current_app as app
import pendulum

from atst.domain.requests import Requests
from atst.domain.users import Users
from atst.domain.authnid import AuthenticationContext
from atst.domain.audit_log import AuditLog
from atst.domain.auth import logout as _logout
from atst.forms.edit_user import EditUserForm


bp = Blueprint("atst", __name__)


@bp.route("/")
def root():
    redirect_url = app.config.get("CAC_URL")
    if request.args.get("next"):
        redirect_url = url.urljoin(
            redirect_url,
            "?{}".format(url.urlencode({"next": request.args.get("next")})),
        )

    return render_template(
        "login.html", redirect=bool(request.args.get("next")), redirect_url=redirect_url
    )


@bp.route("/help")
def helpdocs():
    return render_template("help/index.html")


@bp.route("/home")
def home():
    user = g.current_user

    if user.atat_role_name == "ccpo":
        return redirect(url_for("requests.requests_index"))

    num_workspaces = len(user.workspace_roles)

    if num_workspaces == 0:
        return redirect(url_for("requests.requests_index"))
    elif num_workspaces == 1:
        workspace_role = user.workspace_roles[0]
        workspace_id = workspace_role.workspace.id
        is_request_owner = workspace_role.role.name == "owner"

        if is_request_owner:
            return redirect(
                url_for("workspaces.workspace_reports", workspace_id=workspace_id)
            )
        else:
            return redirect(
                url_for("workspaces.workspace_projects", workspace_id=workspace_id)
            )
    else:
        return redirect(url_for("workspaces.workspaces"))


@bp.route("/styleguide")
def styleguide():
    return render_template("styleguide.html")


@bp.route("/<path:path>")
def catch_all(path):
    return render_template("{}.html".format(path))


def _make_authentication_context():
    return AuthenticationContext(
        crl_cache=app.crl_cache,
        auth_status=request.environ.get("HTTP_X_SSL_CLIENT_VERIFY"),
        sdn=request.environ.get("HTTP_X_SSL_CLIENT_S_DN"),
        cert=request.environ.get("HTTP_X_SSL_CLIENT_CERT"),
    )


def redirect_after_login_url():
    if request.args.get("next"):
        return request.args.get("next")
    else:
        return url_for("atst.home")


@bp.route("/login-redirect")
def login_redirect():
    auth_context = _make_authentication_context()
    auth_context.authenticate()
    user = auth_context.get_user()
    session["user_id"] = user.id

    return redirect(redirect_after_login_url())


@bp.route("/logout")
def logout():
    _logout()
    return redirect(url_for(".root"))


@bp.route("/activity-history")
def activity_history():
    audit_events = AuditLog.get_all_events(g.current_user)
    return render_template("audit_log.html", audit_events=audit_events)


@bp.route("/user")
def user():
    form = EditUserForm(request.form)
    user = g.current_user
    return render_template("user/edit.html", form=form, user=user)


@bp.route("/save_user")
def save_user():
    # no op
    return redirect(url_for(".home"))


@bp.route("/about")
def about():
    return render_template("about.html")
