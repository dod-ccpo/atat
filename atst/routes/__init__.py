from flask import Blueprint, render_template, g, redirect, session, url_for, request
from flask import current_app as app
import pendulum

from atst.domain.requests import Requests
from atst.domain.users import Users
from atst.domain.authnid import AuthenticationContext
from atst.domain.audit_log import AuditLog


bp = Blueprint("atst", __name__)


@bp.route("/")
def root():
    return render_template("root.html")


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


@bp.route("/login-redirect")
def login_redirect():
    auth_context = _make_authentication_context()
    auth_context.authenticate()
    user = auth_context.get_user()
    session["user_id"] = user.id

    return redirect(url_for(".home"))


@bp.route("/logout")
def logout():
    if session.get("user_id"):
        del (session["user_id"])

    return redirect(url_for(".home"))


@bp.route("/activity-history")
def activity_history():
    audit_events = AuditLog.get_all_events(g.current_user)
    return render_template("audit_log.html", audit_events=audit_events)
