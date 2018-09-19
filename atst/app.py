import os
import re
import pathlib
from configparser import ConfigParser
from flask import Flask, request, g
from flask_session import Session
import redis
from unipath import Path
from flask_wtf.csrf import CSRFProtect

from atst.database import db
from atst.assets import environment as assets_environment
from atst.filters import register_filters
from atst.routes import bp
from atst.routes.workspaces import bp as workspace_routes
from atst.routes.requests import requests_bp
from atst.routes.dev import bp as dev_routes
from atst.routes.errors import make_error_pages
from atst.domain.authnid.crl import CRLCache
from atst.domain.auth import apply_authentication
from atst.domain.authz import Authorization
from atst.eda_client import MockEDAClient
from atst.uploader import Uploader


ENV = os.getenv("FLASK_ENV", "dev")


def make_app(config):

    parent_dir = Path().parent

    app = Flask(
        __name__,
        template_folder=parent_dir.child("templates").absolute(),
        static_folder=parent_dir.child("static").absolute(),
    )
    redis = make_redis(config)
    csrf = CSRFProtect()

    app.config.update(config)
    app.config.update({"SESSION_REDIS": redis})

    make_flask_callbacks(app)
    make_crl_validator(app)
    register_filters(app)
    make_eda_client(app)
    make_upload_storage(app)

    db.init_app(app)
    csrf.init_app(app)
    Session(app)
    assets_environment.init_app(app)

    make_error_pages(app)
    app.register_blueprint(bp)
    app.register_blueprint(workspace_routes)
    app.register_blueprint(requests_bp)
    if ENV != "prod":
        app.register_blueprint(dev_routes)

    apply_authentication(app)

    return app


def make_flask_callbacks(app):
    @app.before_request
    def _set_globals():
        g.dev = os.getenv("FLASK_ENV", "dev") == "dev"
        g.matchesPath = lambda href: re.match("^" + href, request.path)
        g.modal = request.args.get("modal", None)
        g.current_user = {
            "id": "cce17030-4109-4719-b958-ed109dbb87c8",
            "first_name": "Amanda",
            "last_name": "Adamson",
            "atat_role": "default",
            "atat_permissions": [],
        }
        g.Authorization = Authorization


def map_config(config):
    return {
        **config["default"],
        "ENV": config["default"]["ENVIRONMENT"],
        "DEBUG": config["default"]["DEBUG"],
        "PORT": int(config["default"]["PORT"]),
        "SQLALCHEMY_DATABASE_URI": config["default"]["DATABASE_URI"],
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": config.getboolean("default", "WTF_CSRF_ENABLED"),
        "PERMANENT_SESSION_LIFETIME": config.getint(
            "default", "PERMANENT_SESSION_LIFETIME"
        ),
    }


def make_config():
    BASE_CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), "../config/base.ini")
    ENV_CONFIG_FILENAME = os.path.join(
        os.path.dirname(__file__), "../config/", "{}.ini".format(ENV.lower())
    )
    OVERRIDE_CONFIG_FILENAME = os.getenv("OVERRIDE_CONFIG_FULLPATH")

    config = ConfigParser()
    config.optionxform = str

    config_files = [BASE_CONFIG_FILENAME, ENV_CONFIG_FILENAME]
    if OVERRIDE_CONFIG_FILENAME:
        config_files.append(OVERRIDE_CONFIG_FILENAME)

    config_files = [BASE_CONFIG_FILENAME, ENV_CONFIG_FILENAME]
    if OVERRIDE_CONFIG_FILENAME:
        config_files.append(OVERRIDE_CONFIG_FILENAME)

    # ENV_CONFIG will override values in BASE_CONFIG.
    config.read(config_files)

    # Check for ENV variables as a final source of overrides
    for confsetting in config.options("default"):
        env_override = os.getenv(confsetting.upper())
        if env_override:
            config.set("default", confsetting, env_override)

    # Assemble DATABASE_URI value
    database_uri = (
        "postgres://"
        + config.get("default", "PGUSER")
        + ":"
        + config.get("default", "PGPASSWORD")
        + "@"
        + config.get("default", "PGHOST")
        + ":"
        + config.get("default", "PGPORT")
        + "/"
        + config.get("default", "PGDATABASE")
    )
    config.set("default", "DATABASE_URI", database_uri)

    return map_config(config)


def make_redis(config):
    return redis.Redis.from_url(config["REDIS_URI"])


def make_crl_validator(app):
    crl_locations = []
    for filename in pathlib.Path(app.config["CRL_DIRECTORY"]).glob("*"):
        crl_locations.append(filename.absolute())
    app.crl_cache = CRLCache(app.config["CA_CHAIN"], crl_locations, logger=app.logger)


def make_eda_client(app):
    app.eda_client = MockEDAClient()


def make_upload_storage(app):
    uploader = Uploader(
        provider=app.config.get("STORAGE_PROVIDER"),
        container=app.config.get("STORAGE_CONTAINER"),
        key=app.config.get("STORAGE_KEY"),
        secret=app.config.get("STORAGE_SECRET"),
    )
    app.uploader = uploader
