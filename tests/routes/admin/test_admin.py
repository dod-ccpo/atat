from flask import url_for

from atat.domain.users import Users
from atat.routes.admin.admin import get_portfolios_from_user, service_branch_label
from atat.utils.localization import translate
from tests.factories import UserFactory


def test_get_portfolios_from_user(user_session, client):
    portfolios = get_portfolios_from_user()
    assert portfolios == "", "if get_portfolios_from_user have not user return empty"


def test_service_branch_label(user_session, client):
    branch_label = service_branch_label()
    assert branch_label == "", "if service_branch_label have not branch id then return empty"
