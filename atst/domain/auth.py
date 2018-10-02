from flask import g, redirect, url_for, session, request

from atst.domain.users import Users


UNPROTECTED_ROUTES = [
    "atst.root",
    "dev.login_dev",
    "atst.login_redirect",
    "atst.unauthorized",
    "atst.helpdocs",
    "static",
    "atst.about",
]


def apply_authentication(app):
    @app.before_request
    # pylint: disable=unused-variable
    def enforce_login():
        user = get_current_user()
        if user:
            g.current_user = user
        elif not _unprotected_route(request):
            return redirect(url_for("atst.root", next=request.path))


def get_current_user():
    user_id = session.get("user_id")
    if user_id:
        return Users.get(user_id)
    else:
        return False


def logout():
    if session.get("user_id"):
        del (session["user_id"])


def _unprotected_route(request):
    if request.endpoint in UNPROTECTED_ROUTES:
        return True
