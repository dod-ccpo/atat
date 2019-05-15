import pytest
from flask import url_for
from copy import copy
from tests.factories import UserFactory


@pytest.fixture
def csrf_enabled_app(app):
    app.config.update({"WTF_CSRF_ENABLED": True})
    yield app
    app.config.update({"WTF_CSRF_ENABLED": False})


def test_csrf_error(csrf_enabled_app, client):
    response = client.post(
        url_for("users.user"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="csrf_token=invalid_token",
        follow_redirects=True,
    )

    body = response.data.decode()
    assert "Session Expired" in body
    assert "Log in Required" in body


def test_errors_generate_notifications(app, client, user_session, notification_sender):
    user_session(UserFactory.create())
    new_app = copy(app)

    @new_app.route("/throw")
    def throw():
        raise ValueError()

    new_app.test_client().get("/throw")

    notification_sender.send.assert_called_once()
