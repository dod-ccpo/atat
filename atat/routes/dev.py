import random
from urllib.parse import urlparse

from flask import (
    Blueprint,
    request,
    redirect,
    render_template,
    url_for,
    current_app as app,
    session,
)
from onelogin.saml2.auth import OneLogin_Saml2_Auth
import pendulum

from . import redirect_after_login_url, current_user_setup
from atat.domain.exceptions import AlreadyExistsError, NotFoundError
from atat.domain.users import Users
from atat.domain.permission_sets import PermissionSets
from atat.forms.data import SERVICE_BRANCHES
from atat.jobs import send_mail
from atat.utils import pick
from atat.saml_helpers import do_login_saml


bp = Blueprint("dev", __name__)

_ALL_PERMS = [
    PermissionSets.VIEW_PORTFOLIO,
    PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
    PermissionSets.VIEW_PORTFOLIO_FUNDING,
    PermissionSets.VIEW_PORTFOLIO_REPORTS,
    PermissionSets.VIEW_PORTFOLIO_ADMIN,
    PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT,
    PermissionSets.EDIT_PORTFOLIO_FUNDING,
    PermissionSets.EDIT_PORTFOLIO_REPORTS,
    PermissionSets.EDIT_PORTFOLIO_ADMIN,
    PermissionSets.PORTFOLIO_POC,
    PermissionSets.VIEW_AUDIT_LOG,
    PermissionSets.MANAGE_CCPO_USERS,
]


def random_service_branch():
    return random.choice([k for k, v in SERVICE_BRANCHES if k])  # nosec


_DEV_USERS = {
    "sam": {
        "dod_id": "6346349876",
        "first_name": "Sam",
        "last_name": "Stevenson",
        "permission_sets": _ALL_PERMS,
        "email": "sam@example.com",
        "service_branch": random_service_branch(),
        "phone_number": "1234567890",
        "citizenship": "United States",
        "designation": "Military",
        "date_latest_training": pendulum.date(2018, 1, 1),
    },
    "amanda": {
        "dod_id": "2345678901",
        "first_name": "Amanda",
        "last_name": "Adamson",
        "email": "amanda@example.com",
        "service_branch": random_service_branch(),
        "phone_number": "1234567890",
        "citizenship": "United States",
        "designation": "Military",
        "date_latest_training": pendulum.date(2018, 1, 1),
    },
    "brandon": {
        "dod_id": "3456789012",
        "first_name": "Brandon",
        "last_name": "Buchannan",
        "email": "brandon@example.com",
        "service_branch": random_service_branch(),
        "phone_number": "1234567890",
        "citizenship": "United States",
        "designation": "Military",
        "date_latest_training": pendulum.date(2018, 1, 1),
    },
    "christina": {
        "dod_id": "4567890123",
        "first_name": "Christina",
        "last_name": "Collins",
        "email": "christina@example.com",
        "service_branch": random_service_branch(),
        "phone_number": "1234567890",
        "citizenship": "United States",
        "designation": "Military",
        "date_latest_training": pendulum.date(2018, 1, 1),
    },
    "dominick": {
        "dod_id": "5678901234",
        "first_name": "Dominick",
        "last_name": "Domingo",
        "email": "dominick@example.com",
        "service_branch": random_service_branch(),
        "phone_number": "1234567890",
        "citizenship": "United States",
        "designation": "Military",
        "date_latest_training": pendulum.date(2018, 1, 1),
    },
    "erica": {
        "dod_id": "6789012345",
        "first_name": "Erica",
        "last_name": "Eichner",
        "email": "erica@example.com",
        "service_branch": random_service_branch(),
        "phone_number": "1234567890",
        "citizenship": "United States",
        "designation": "Military",
        "date_latest_training": pendulum.date(2018, 1, 1),
    },
}


class IncompleteInfoError(Exception):
    @property
    def message(self):
        return "You must provide each of: first_name, last_name and dod_id"


@bp.route("/login-dev")
def login_dev():
    dod_id = request.args.get("dod_id", None)

    if dod_id is not None:
        user = Users.get_by_dod_id(dod_id)
    else:
        role = request.args.get("username", "amanda")
        user_data = _DEV_USERS[role]
        user = Users.get_or_create_by_dod_id(
            user_data["dod_id"],
            **pick(
                [
                    "permission_sets",
                    "first_name",
                    "last_name",
                    "email",
                    "service_branch",
                    "phone_number",
                    "citizenship",
                    "designation",
                    "date_latest_training",
                ],
                user_data,
            ),
        )

    current_user_setup(user)
    return redirect(redirect_after_login_url())


@bp.route("/dev-new-user")
def dev_new_user():
    first_name = request.args.get("first_name", None)
    last_name = request.args.get("last_name", None)
    dod_id = request.args.get("dod_id", None)

    if None in [first_name, last_name, dod_id]:
        raise IncompleteInfoError()

    try:
        Users.get_by_dod_id(dod_id)
        raise AlreadyExistsError("User with dod_id {}".format(dod_id))
    except NotFoundError:
        pass

    new_user = {"first_name": first_name, "last_name": last_name}

    created_user = Users.create(dod_id, **new_user)

    current_user_setup(created_user)
    return redirect(redirect_after_login_url())


@bp.route("/test-email")
def test_email():
    send_mail.delay(
        [request.args.get("to")], request.args.get("subject"), request.args.get("body")
    )

    return redirect(url_for("dev.messages"))


@bp.route("/messages")
def messages():
    return render_template("dev/emails.html", messages=app.mailer.messages)


@bp.route("/login-dev-saml", methods=["GET", "POST"])
    return do_login_saml()
