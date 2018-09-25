from flask import g, redirect, url_for, session, request

from atst.domain.users import Users


UNPROTECTED_ROUTES = [
    "atst.root",
    "dev.login_dev",
    "atst.login_redirect",
    "atst.unauthorized",
    "atst.helpdocs",
    "static",
]


def apply_authentication(app):
    @app.before_request
    # pylint: disable=unused-variable
    def enforce_login():

        if not _unprotected_route(request):
            user = get_current_user()
            if user:
                g.current_user = user

            else:
                return redirect(url_for("atst.root"))


def get_current_user():
    user_id = session.get("user_id")
    if user_id:
        return Users.get(user_id)
    else:
        return False


def _unprotected_route(request):
    if request.endpoint in UNPROTECTED_ROUTES:
        return True
