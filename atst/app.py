import os
import re
from configparser import ConfigParser
from datetime import datetime
from flask import Flask, request, g, session, url_for as flask_url_for
from flask_session import Session
import redis
from unipath import Path
from flask_wtf.csrf import CSRFProtect
from urllib.parse import urljoin

from atst.database import db
from atst.assets import environment as assets_environment
from atst.filters import register_filters
from atst.routes import bp
from atst.routes.portfolios import portfolios_bp as portfolio_routes
from atst.routes.task_orders import task_orders_bp
from atst.routes.applications import applications_bp
from atst.routes.dev import bp as dev_routes
from atst.routes.users import bp as user_routes
from atst.routes.errors import make_error_pages
from atst.routes.ccpo import bp as ccpo_routes
from atst.domain.authnid.crl import CRLCache, NoOpCRLCache
from atst.domain.auth import apply_authentication
from atst.domain.authz import Authorization
from atst.domain.csp import make_csp_provider
from atst.domain.portfolios import Portfolios
from atst.models.permissions import Permissions
from atst.queue import celery, update_celery
from atst.utils import mailer
from atst.utils.form_cache import FormCache
from atst.utils.json import CustomJSONEncoder, sqlalchemy_dumps
from atst.utils.notification_sender import NotificationSender
from atst.utils.session_limiter import SessionLimiter

from logging.config import dictConfig
from atst.utils.logging import JsonFormatter, RequestContextFilter

from atst.utils.context_processors import assign_resources


ENV = os.getenv("FLASK_ENV", "dev")


def make_app(config):
    if ENV == "prod" or config.get("LOG_JSON"):
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

    app.config.update(config)
    app.config.update({"SESSION_REDIS": app.redis})

    update_celery(celery, app)

    make_flask_callbacks(app)
    register_filters(app)
    register_jinja_globals(app)
    make_csp_provider(app, config.get("CSP", "mock"))
    make_crl_validator(app)
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

    if ENV != "prod":
        app.register_blueprint(dev_routes)

    app.form_cache = FormCache(app.redis)

    apply_authentication(app)
    set_default_headers(app)

    @app.before_request
    def _set_resources():
        assign_resources(request.view_args)

    return app


def make_flask_callbacks(app):
    @app.before_request
    def _set_globals():
        g.current_user = None
        g.dev = os.getenv("FLASK_ENV", "dev") == "dev"
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

    @app.after_request
    def _set_security_headers(response):
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Access-Control-Allow-Origin"] = app.config.get("CDN_ORIGIN")

        if ENV == "dev":
            response.headers[
                "Content-Security-Policy"
            ] = "default-src 'self' 'unsafe-eval' 'unsafe-inline'; connect-src *"
        else:
            response.headers[
                "Content-Security-Policy"
            ] = f"default-src 'self' 'unsafe-eval' 'unsafe-inline' {blob_storage_url} {static_url}"

        return response


def map_config(config):
    return {
        **config["default"],
        "USE_AUDIT_LOG": config["default"].getboolean("USE_AUDIT_LOG"),
        "ENV": config["default"]["ENVIRONMENT"],
        "BROKER_URL": config["default"]["REDIS_URI"],
        "DEBUG": config["default"].getboolean("DEBUG"),
        "DEBUG_MAILER": config["default"].getboolean("DEBUG_MAILER"),
        "SQLALCHEMY_ECHO": config["default"].getboolean("SQLALCHEMY_ECHO"),
        "PORT": int(config["default"]["PORT"]),
        "SQLALCHEMY_DATABASE_URI": config["default"]["DATABASE_URI"],
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "json_serializer": sqlalchemy_dumps,
            "connect_args": {
                "sslmode": config["default"]["PGSSLMODE"],
                "sslrootcert": config["default"]["PGSSLROOTCERT"],
            },
        },
        "WTF_CSRF_ENABLED": config.getboolean("default", "WTF_CSRF_ENABLED"),
        "PERMANENT_SESSION_LIFETIME": config.getint(
            "default", "PERMANENT_SESSION_LIFETIME"
        ),
        "DISABLE_CRL_CHECK": config.getboolean("default", "DISABLE_CRL_CHECK"),
        "CRL_FAIL_OPEN": config.getboolean("default", "CRL_FAIL_OPEN"),
        "LOG_JSON": config.getboolean("default", "LOG_JSON"),
        "LIMIT_CONCURRENT_SESSIONS": config.getboolean(
            "default", "LIMIT_CONCURRENT_SESSIONS"
        ),
        # Store the celery task results in a database table (celery_taskmeta)
        "CELERY_RESULT_BACKEND": "db+{}".format(config.get("default", "DATABASE_URI")),
        # Do not automatically delete results (by default, Celery will do this
        # with a Beat job once a day)
        "CELERY_RESULT_EXPIRES": 0,
        "CELERY_RESULT_EXTENDED": True,
        "CONTRACT_START_DATE": datetime.strptime(
            config.get("default", "CONTRACT_START_DATE"), "%Y-%m-%d"
        ).date(),
        "CONTRACT_END_DATE": datetime.strptime(
            config.get("default", "CONTRACT_END_DATE"), "%Y-%m-%d"
        ).date(),
    }


def make_config(direct_config=None):
    BASE_CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), "../config/base.ini")
    ENV_CONFIG_FILENAME = os.path.join(
        os.path.dirname(__file__), "../config/", "{}.ini".format(ENV.lower())
    )
    OVERRIDE_CONFIG_DIRECTORY = os.getenv("OVERRIDE_CONFIG_DIRECTORY")

    config = ConfigParser(allow_no_value=True)
    config.optionxform = str

    config_files = [BASE_CONFIG_FILENAME, ENV_CONFIG_FILENAME]

    # ENV_CONFIG will override values in BASE_CONFIG.
    config.read(config_files)

    if OVERRIDE_CONFIG_DIRECTORY:
        apply_config_from_directory(OVERRIDE_CONFIG_DIRECTORY, config)

    # Check for ENV variables as a final source of overrides
    apply_config_from_environment(config)

    # override if a dictionary of options has been given
    if direct_config:
        config.read_dict({"default": direct_config})

    # Assemble DATABASE_URI value
    database_uri = "postgresql://{}:{}@{}:{}/{}".format(  # pragma: allowlist secret
        config.get("default", "PGUSER"),
        config.get("default", "PGPASSWORD"),
        config.get("default", "PGHOST"),
        config.get("default", "PGPORT"),
        config.get("default", "PGDATABASE"),
    )
    config.set("default", "DATABASE_URI", database_uri)

    # Assemble REDIS_URI value
    redis_uri = "redis{}://{}:{}@{}".format(  # pragma: allowlist secret
        ("s" if config["default"].getboolean("REDIS_TLS") else ""),
        (config.get("default", "REDIS_USER") or ""),
        (config.get("default", "REDIS_PASSWORD") or ""),
        config.get("default", "REDIS_HOST"),
    )
    config.set("default", "REDIS_URI", redis_uri)

    return map_config(config)


def apply_config_from_directory(config_dir, config, section="default"):
    """
    Loop files in a directory, check if the names correspond to
    known config values, and apply the file contents as the value
    for that setting if they do.
    """
    for confsetting in os.listdir(config_dir):
        if confsetting in config.options(section):
            full_path = os.path.join(config_dir, confsetting)
            with open(full_path, "r") as conf_file:
                config.set(section, confsetting, conf_file.read().strip())

    return config


def apply_config_from_environment(config, section="default"):
    """
    Loops all the configuration settins in a given section of a
    config object and checks whether those settings also exist as
    environment variables. If so, it applies the environment
    variables value as the new configuration setting value.
    """
    for confsetting in config.options(section):
        env_override = os.getenv(confsetting.upper())
        if env_override:
            config.set(section, confsetting, env_override)

    return config


def make_redis(app, config):
    r = redis.Redis.from_url(config["REDIS_URI"])
    app.redis = r


def make_crl_validator(app):
    if app.config.get("DISABLE_CRL_CHECK"):
        app.crl_cache = NoOpCRLCache(logger=app.logger)
    else:
        crl_dir = app.config["CRL_STORAGE_CONTAINER"]
        if not os.path.isdir(crl_dir):
            os.makedirs(crl_dir, exist_ok=True)

        app.crl_cache = CRLCache(app.config["CA_CHAIN"], crl_dir, logger=app.logger,)


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

    def _url_for(endpoint, **values):
        if endpoint == "static":
            filename = values["filename"]
            return urljoin(static_url, filename)
        else:
            return flask_url_for(endpoint, **values)

    app.jinja_env.globals["url_for"] = _url_for
