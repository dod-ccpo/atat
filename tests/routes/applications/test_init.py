from flask import url_for, get_flashed_messages

from tests.factories import *


def test_environment_access_with_env_role(client, user_session):
    user = UserFactory.create()
    environment = EnvironmentFactory.create()
    app_role = ApplicationRoleFactory.create(
        user=user, application=environment.application
    )
    EnvironmentRoleFactory.create(application_role=app_role, environment=environment)
    user_session(user)
    response = client.get(
        url_for("applications.access_environment", environment_id=environment.id)
    )
    assert response.status_code == 302
    assert "csp-environment-access" in response.location


def test_environment_access_with_no_role(client, user_session):
    user = UserFactory.create()
    environment = EnvironmentFactory.create()
    user_session(user)
    response = client.get(
        url_for("applications.access_environment", environment_id=environment.id)
    )
    assert response.status_code == 404
