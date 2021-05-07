from flask import url_for

from atat.domain.users import Users
from atat.routes.admin.admin import get_portfolios_from_user, service_branch_label
from atat.utils.localization import translate
from tests.factories import UserFactory


def test_get_portfolios_from_user(user_session, client):
    portfolios = get_portfolios_from_user()
    assert (
        portfolios == ""
    ), "A user without portfolios should result in an empty string"


def test_service_branch_label(user_session, client):
    branch_label = service_branch_label()
    branch_label_wrong = service_branch_label(service_branch="loren")
    air_force_label = translate("forms.portfolio.defense_component.choices.air_force")
    branch_label_air_force = service_branch_label(service_branch="air_force")
    assert (
        branch_label == ""
    ), "if service_branch_label have not branch id then return empty string"
    assert (
        air_force_label == branch_label_air_force
    ), "the liable need to be the same that in the translation file."
    assert branch_label_wrong == "", "the liable is not valid return empty string."


def test_user_page(user_session, client):
    ccpo = UserFactory.create_ccpo()
    user_session(ccpo)
    response = client.get(url_for("admin.user_page", user_id=ccpo.id))
    assert ccpo.email in response.data.decode(), "email is not present on user page."
