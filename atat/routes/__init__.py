import urllib.parse as url
from flask import (
    Blueprint,
    render_template,
    g,
    redirect,
    session,
    url_for,
    request,
    make_response,
    current_app as app,
)

from jinja2.exceptions import TemplateNotFound
import pendulum
import os
from werkzeug.exceptions import NotFound, MethodNotAllowed
from werkzeug.routing import RequestRedirect


from atat.domain.users import Users
from atat.domain.authnid import AuthenticationContext
from atat.domain.auth import logout as _logout
from atat.domain.exceptions import UnauthenticatedError
from atat.utils.flash import formatted_flash as flash

bp = Blueprint("atat", __name__)


@bp.route("/")
def root():
    if g.current_user:
        return redirect(url_for(".home"))

    redirect_url = app.config.get("CAC_URL")
    if request.args.get("next"):
        redirect_url = url.urljoin(
            redirect_url,
            "?{}".format(url.urlencode({"next": request.args.get("next")})),
        )
        flash("login_next")

    return render_template("login.html", redirect_url=redirect_url)


@bp.route("/home")
def home():
    return render_template("home.html")


def _client_s_dn():
    return request.environ.get("HTTP_X_SSL_CLIENT_S_DN")


def _make_authentication_context():
    return AuthenticationContext(
        crl_cache=app.crl_cache,
        auth_status=request.environ.get("HTTP_X_SSL_CLIENT_VERIFY"),
        sdn=_client_s_dn(),
        cert=request.environ.get("HTTP_X_SSL_CLIENT_CERT"),
    )


def redirect_after_login_url():
    returl = request.args.get("next")
    if match_url_pattern(returl):
        param_name = request.args.get(app.form_cache.PARAM_NAME)
        if param_name:
            returl += "?" + url.urlencode({app.form_cache.PARAM_NAME: param_name})
        return returl
    else:
        return url_for("atat.home")


def match_url_pattern(url, method="GET"):
    """Ensure a url matches a url pattern in the flask app
    inspired by https://stackoverflow.com/questions/38488134/get-the-flask-view-function-that-matches-a-url/38488506#38488506
    """
    server_name = app.config.get("SERVER_NAME") or "localhost"
    adapter = app.url_map.bind(server_name=server_name)

    try:
        match = adapter.match(url, method=method)
    except RequestRedirect as e:
        # recursively match redirects
        return match_url_pattern(e.new_url, method)
    except (MethodNotAllowed, NotFound):
        # no match
        return None

    if match[0] in app.view_functions:
        return url


def current_user_setup(user):
    session["user_id"] = user.id
    session["last_login"] = user.last_login
    app.session_limiter.on_login(user)
    app.logger.info("authentication succeeded for user with EDIPI %s", user.dod_id)
    Users.update_last_login(user)


@bp.route("/login-redirect")
def login_redirect():
    try:
        auth_context = _make_authentication_context()
        auth_context.authenticate()

        user = auth_context.get_user()
        current_user_setup(user)
    except UnauthenticatedError as err:
        app.logger.info(
            "authentication failed for subject distinguished name %s", _client_s_dn()
        )
        raise err

    return redirect(redirect_after_login_url())


@bp.route("/logout")
def logout():
    _logout()
    response = make_response(redirect(url_for(".root")))
    response.set_cookie("expandSidenav", "", expires=0)
    flash("logged_out")
    return response


@bp.route("/about")
def about():
    return render_template("about.html")
