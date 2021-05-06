import re
from logging.config import dictConfig
from urllib.parse import urljoin

import redis
from flask import Flask, g, request, session
from flask import url_for as flask_url_for
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from unipath import Path

from atat.assets import environment as assets_environment
from atat.database import db
from atat.debug import setup_debug_toolbar
from atat.domain.auth import apply_authentication
from atat.domain.authz import Authorization
from atat.domain.csp import make_csp_provider
from atat.domain.portfolios import Portfolios
from atat.filters import register_filters
from atat.models.permissions import Permissions
from atat.queue import celery, update_celery
from atat.routes import bp
from atat.routes.applications import applications_bp
from atat.routes.ccpo import bp as ccpo_routes
from atat.routes.admin.admin import bp as admin_routes
from atat.routes.dev import dev_bp as dev_routes
from atat.routes.dev import local_access_bp
from atat.routes.errors import make_error_pages
from atat.routes.portfolios import portfolios_bp as portfolio_routes
from atat.routes.task_orders import task_orders_bp
from atat.routes.users import bp as user_routes
from atat.utils import mailer
from atat.utils.context_processors import assign_resources
from atat.utils.environment import ApplicationEnvironment
from atat.utils.form_cache import FormCache
from atat.utils.json import CustomJSONEncoder
from atat.utils.logging import JsonFormatter, RequestContextFilter
from atat.utils.notification_sender import NotificationSender
from atat.utils.session_limiter import SessionLimiter


def make_app(config):
    environment_name = ApplicationEnvironment(config["ENV"])

    if environment_name is ApplicationEnvironment.PRODUCTION or config.get("LOG_JSON"):
        apply_json_logger()

    parent_dir = Path().parent

    app = Flask(
        __name__,
        template_folder=str(object=parent_dir.child("templates").absolute()),
        static_folder=str(object=parent_dir.child("static").absolute()),
    )
    app.json_encoder = CustomJSONEncoder
    make_redis(app, config)
    csrf = CSRFProtect()
    # These routes are exempted in order to allow SAML integration
    csrf.exempt("atat.routes.dev.login_dev")
    csrf.exempt("atat.routes.login")
    csrf.exempt("atat.routes.handle_login_response")

    app.config.update(config)
    app.config.update({"SESSION_REDIS": app.redis})

    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    update_celery(celery, app)

    make_flask_callbacks(app)
    register_filters(app)
    register_jinja_globals(app)
    make_csp_provider(app, config.get("CSP", "mock"))
    make_mailer(app)
    make_notification_sender(app)

    db.init_app(app)
    csrf.init_app(app)
    Session(app)
    make_session_limiter(app, session, config)
    assets_environment.init_app(app)

    make_error_pages(app)
    app.register_blueprint(bp)
    app.register_blueprint(portfolio_routes)
    app.register_blueprint(task_orders_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(user_routes)
    app.register_blueprint(ccpo_routes)
    app.register_blueprint(admin_routes)

    if environment_name is not ApplicationEnvironment.PRODUCTION:
        # Activate the dev routes
        app.register_blueprint(dev_routes)
        # Activate debug toolbar if it is the right env
        setup_debug_toolbar(app, environment_name.value)
        if app.config.get("ALLOW_LOCAL_ACCESS"):
            # active dev route that are only available on local
            app.register_blueprint(local_access_bp)

    app.form_cache = FormCache(app.redis)

    apply_authentication(app)
    set_default_headers(app)

    @app.before_request
    def _set_resources():
        assign_resources(request.view_args)

    return app


def make_flask_callbacks(app):
    environment_name = ApplicationEnvironment(app.config.get("ENV"))

    @app.before_request
    def _set_globals():
        g.current_user = None
        g.dev = environment_name is ApplicationEnvironment.DEVELOPMENT
        g.matchesPath = lambda href: re.search(href, request.full_path)
        g.modal = request.args.get("modal", None)
        g.Authorization = Authorization
        g.Permissions = Permissions

    @app.context_processor
    def _portfolios():
        if not g.current_user:
            return {}

        portfolios = Portfolios.for_user(g.current_user)
        return {"portfolios": portfolios}

    @app.after_request
    def _cleanup(response):
        g.current_user = None
        g.portfolio = None
        g.application = None
        g.task_order = None
        return response


def set_default_headers(app):  # pragma: no cover
    static_url = app.config.get("STATIC_URL")
    blob_storage_url = app.config.get("BLOB_STORAGE_URL")
    environment_name = ApplicationEnvironment(app.config.get("ENV"))

    @app.after_request
    def _set_security_headers(response):

        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains; always"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Access-Control-Allow-Origin"] = app.config.get("CDN_ORIGIN")

        set_response_content_security_policy_headers(
            response,
            "default-src 'self' 'unsafe-eval' 'unsafe-inline'; connect-src *"
            if environment_name is ApplicationEnvironment.DEVELOPMENT
            else f"default-src 'self' 'unsafe-eval' 'unsafe-inline' {blob_storage_url} {static_url}",
        )

        return response


def set_response_content_security_policy_headers(
    response, content_security_policy_headers
):
    response.headers["Content-Security-Policy"] = content_security_policy_headers
    response.headers["X-Content-Security-Policy"] = content_security_policy_headers


def make_redis(app, config):
    r = redis.Redis.from_url(config["REDIS_URI"])
    app.redis = r


def make_mailer(app):
    if app.config["DEBUG"] or app.config["DEBUG_MAILER"]:
        mailer_connection = mailer.RedisConnection(app.redis)
    else:
        mailer_connection = mailer.SMTPConnection(
            server=app.config.get("MAIL_SERVER"),
            port=app.config.get("MAIL_PORT"),
            username=app.config.get("MAIL_SENDER"),
            password=app.config.get("MAIL_PASSWORD"),
            use_tls=app.config.get("MAIL_TLS"),
            debug_smtp=app.config.get("DEBUG_SMTP"),
        )
    sender = app.config.get("MAIL_SENDER")
    app.mailer = mailer.Mailer(mailer_connection, sender)


def make_notification_sender(app):
    app.notification_sender = NotificationSender()


def make_session_limiter(app, session, config):
    app.session_limiter = SessionLimiter(config, session, app.redis)


def apply_json_logger():
    dictConfig(
        {
            "version": 1,
            "formatters": {"default": {"()": lambda *a, **k: JsonFormatter()}},
            "filters": {"requests": {"()": lambda *a, **k: RequestContextFilter()}},
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                    "filters": ["requests"],
                }
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
        }
    )


def register_jinja_globals(app):
    static_url = app.config.get("STATIC_URL", "/static/")
    app_version = app.config.get("APP_VERSION", "")
    git_sha = app.config.get("GIT_SHA", "")

    def _url_for(endpoint, **values):
        if endpoint == "static":
            filename = values["filename"]
            return urljoin(static_url, filename)
        else:
            return flask_url_for(endpoint, **values)

    app.jinja_env.globals.update(
        {
            "url_for": _url_for,
            "service_desk_url": app.config.get("SERVICE_DESK_URL"),
            "build_info": f"{app_version} {git_sha}",
        }
    )
