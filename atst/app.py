import os
from configparser import ConfigParser
import tornado.web
from tornado.web import url
from redis import StrictRedis

from atst.handlers.main import Main
from atst.handlers.root import Root
from atst.handlers.login_redirect import LoginRedirect
from atst.handlers.workspaces import Workspaces
from atst.handlers.workspace import Workspace
from atst.handlers.workspace_members import WorkspaceMembers
from atst.handlers.request import Request
from atst.handlers.request_financial_verification import RequestFinancialVerification
from atst.handlers.request_new import RequestNew
from atst.handlers.request_submit import RequestsSubmit
from atst.handlers.dev import Dev
from atst.home import home
from atst.api_client import ApiClient
from atst.sessions import RedisSessions
from atst import ui_modules
from atst import ui_methods
from atst.database import make_db

ENV = os.getenv("TORNADO_ENV", "dev")

def make_app(config, deps, **kwargs):

    routes = [
        url(r"/", Root, {"page": "root"}, name="root"),
        url(
            r"/login-redirect",
            LoginRedirect,
            {"sessions": deps["sessions"], "authnid_client": deps["authnid_client"], "authz_client": deps["authz_client"]},
            name="login_redirect",
        ),
        url(r"/home", Main, {"page": "home"}, name="home"),
        url(
            r"/styleguide",
            Main,
            {"page": "styleguide"},
            name="styleguide",
        ),
        url(
            r"/workspaces/blank",
            Main,
            {"page": "workspaces_blank"},
            name="workspaces_blank",
        ),
        url(
            r"/workspaces",
            Workspaces,
            {"page": "workspaces", "authz_client": deps["authz_client"]},
            name="workspaces",
        ),
        url(
            r"/requests",
            Request,
            {"page": "requests", "db_session": deps["db_session"]},
            name="requests",
        ),
        url(
            r"/requests/new",
            RequestNew,
            {
                "page": "requests_new",
                "requests_client": deps["requests_client"],
                "fundz_client": deps["fundz_client"],
            },
            name="request_new",
        ),
        url(
            r"/requests/new/([0-9])",
            RequestNew,
            {
                "page": "requests_new",
                "requests_client": deps["requests_client"],
                "fundz_client": deps["fundz_client"],
            },
            name="request_form_new",
        ),
        url(
            r"/requests/new/([0-9])/(\S+)",
            RequestNew,
            {
                "page": "requests_new",
                "requests_client": deps["requests_client"],
                "fundz_client": deps["fundz_client"],
            },
            name="request_form_update",
        ),
        url(
            r"/requests/submit/(\S+)",
            RequestsSubmit,
            {"requests_client": deps["requests_client"]},
            name="requests_submit",
        ),
        # Dummy request/approval screen
        url(
            r"/request/approval",
            Main,
            {"page": "request_approval"},
            name="request_approval"
        ),
        url(
            r"/requests/verify/(\S+)",
            RequestFinancialVerification,
            {
                "page": "financial_verification",
                "requests_client": deps["requests_client"],
                "fundz_client": deps["fundz_client"],
            },
            name="financial_verification",
        ),
        url(
            r"/requests/financial_verification_submitted",
            Main,
            {"page": "requests/financial_verification_submitted"},
            name="financial_verification_submitted",
        ),
        url(r"/users", Main, {"page": "users"}, name="users"),
        url(r"/reports", Main, {"page": "reports"}, name="reports"),
        url(r"/calculator", Main, {"page": "calculator"}, name="calculator"),
        url(r"/workspaces/(\S+)/members", WorkspaceMembers, {}, name="workspace_members"),
        url(r"/workspaces/(\S+)/projects", Workspace, {}, name="workspace_projects"),
        url(r"/workspaces/123456/projects/789/edit", Main, {"page": "project_edit"}, name="project_edit"),
    ]

    if not ENV == "production":
        routes += [
            url(
                r"/login-dev",
                Dev,
                {"action": "login", "sessions": deps["sessions"], "authz_client": deps["authz_client"]},
                name="dev-login",
            )
        ]

    app = tornado.web.Application(
        routes,
        login_url="/",
        template_path=home.child("templates"),
        static_path=home.child("static"),
        cookie_secret=config["default"]["COOKIE_SECRET"],
        debug=config["default"].getboolean("DEBUG"),
        ui_modules=ui_modules,
        ui_methods=ui_methods,
        **kwargs,
    )
    app.config = config
    app.sessions = deps["sessions"]
    return app


def make_deps(config):
    # we do not want to do SSL verify services in test and development
    validate_cert = ENV == "production"
    redis_client = StrictRedis.from_url(
        config["default"]["REDIS_URI"], decode_responses=True
    )

    return {
        "db_session": make_db(config),
        "authz_client": ApiClient(
            config["default"]["AUTHZ_BASE_URL"],
            api_version="v1",
            validate_cert=validate_cert,
        ),
        "authnid_client": ApiClient(
            config["default"]["AUTHNID_BASE_URL"],
            api_version="v1",
            validate_cert=validate_cert,
        ),
        "fundz_client": ApiClient(
            config["default"]["FUNDZ_BASE_URL"],
            validate_cert=validate_cert,
        ),
        "requests_client": ApiClient(
            config["default"]["REQUESTS_QUEUE_BASE_URL"],
            api_version="v1",
            validate_cert=validate_cert,
        ),
        "sessions": RedisSessions(
            redis_client, config["default"]["SESSION_TTL_SECONDS"]
        ),
    }


def make_config():
    BASE_CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), "../config/base.ini")
    ENV_CONFIG_FILENAME = os.path.join(
        os.path.dirname(__file__), "../config/", "{}.ini".format(ENV.lower())
    )
    config = ConfigParser()

    # ENV_CONFIG will override values in BASE_CONFIG.
    config.read([BASE_CONFIG_FILENAME, ENV_CONFIG_FILENAME])
    return config
