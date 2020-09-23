import pytest
from flask import url_for

from atat.utils.localization import translate
from tests.factories import UserFactory


def test_home_route(client, user_session):
    user = UserFactory.create()
    user_session(user)

    response = client.get(url_for("atat.home"))

    assert response.status_code == 200
    assert translate("home.add_portfolio_button_text").encode("utf8") in response.data
