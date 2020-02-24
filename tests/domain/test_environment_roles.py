import pytest

from atat.domain.environment_roles import EnvironmentRoles
from atat.models import EnvironmentRole, ApplicationRoleStatus

from tests.factories import *


@pytest.fixture
def application_role():
    user = UserFactory.create()
    application = ApplicationFactory.create()
    return ApplicationRoleFactory.create(application=application, user=user)


@pytest.fixture
def environment(application_role):
    return EnvironmentFactory.create(application=application_role.application)


def test_create(application_role, environment, monkeypatch):

    environment_role = EnvironmentRoles.create(
        application_role, environment, "network admin"
    )
    assert environment_role.application_role == application_role
    assert environment_role.environment == environment
    assert environment_role.role == "network admin"


def test_get(application_role, environment):
    EnvironmentRoleFactory.create(
        application_role=application_role, environment=environment
    )

    environment_role = EnvironmentRoles.get(application_role.id, environment.id)
    assert environment_role
    assert environment_role.application_role == application_role
    assert environment_role.environment == environment


def test_get_by_user_and_environment(application_role, environment):
    expected_role = EnvironmentRoleFactory.create(
        application_role=application_role, environment=environment
    )
    actual_role = EnvironmentRoles.get_by_user_and_environment(
        application_role.user.id, environment.id
    )
    assert expected_role == actual_role


def test_delete(application_role, environment, monkeypatch):
    env_role = EnvironmentRoleFactory.create(
        application_role=application_role, environment=environment
    )
    assert EnvironmentRoles.delete(application_role.id, environment.id)
    assert not EnvironmentRoles.delete(application_role.id, environment.id)


def test_get_for_application_member(application_role, environment):
    EnvironmentRoleFactory.create(
        application_role=application_role, environment=environment
    )

    roles = EnvironmentRoles.get_for_application_member(application_role.id)
    assert len(roles) == 1
    assert roles[0].environment == environment
    assert roles[0].application_role == application_role


def test_get_for_application_member_does_not_return_deleted(
    application_role, environment
):
    EnvironmentRoleFactory.create(
        application_role=application_role, environment=environment, deleted=True
    )

    roles = EnvironmentRoles.get_for_application_member(application_role.id)
    assert len(roles) == 0


def test_disable_completed(application_role, environment):
    environment_role = EnvironmentRoleFactory.create(
        application_role=application_role,
        environment=environment,
        status=EnvironmentRole.Status.COMPLETED,
    )

    environment_role = EnvironmentRoles.disable(environment_role.id)

    assert environment_role.disabled


def test_disable_checks_env_provisioning_status(session):
    environment = EnvironmentFactory.create()
    assert not environment.cloud_id
    env_role1 = EnvironmentRoleFactory.create(environment=environment)
    env_role1 = EnvironmentRoles.disable(env_role1.id)
    assert env_role1.disabled

    environment.cloud_id = "cloud-id"
    session.add(environment)
    session.commit()
    session.refresh(environment)

    assert environment.cloud_id
    env_role2 = EnvironmentRoleFactory.create(environment=environment)
    env_role2 = EnvironmentRoles.disable(env_role2.id)
    assert env_role2.disabled


def test_disable_checks_env_role_provisioning_status():
    environment = EnvironmentFactory.create(cloud_id="cloud-id")
    environment.portfolio.csp_data = {"tenant_id": uuid4().hex}
    env_role1 = EnvironmentRoleFactory.create(environment=environment)
    assert not env_role1.cloud_id
    env_role1 = EnvironmentRoles.disable(env_role1.id)
    assert env_role1.disabled

    env_role2 = EnvironmentRoleFactory.create(
        environment=environment, cloud_id="123456"
    )
    assert env_role2.cloud_id
    env_role2 = EnvironmentRoles.disable(env_role2.id)
    assert env_role2.disabled


def test_get_for_update(application_role, environment):
    EnvironmentRoleFactory.create(
        application_role=application_role, environment=environment, deleted=True
    )
    role = EnvironmentRoles.get_for_update(application_role.id, environment.id)
    assert role
    assert role.application_role == application_role
    assert role.environment == environment
    assert role.deleted


def test_for_user(application_role):
    portfolio = application_role.application.portfolio
    user = application_role.user
    # create roles for 2 environments associated with application_role fixture
    env_role_1 = EnvironmentRoleFactory.create(application_role=application_role)
    env_role_2 = EnvironmentRoleFactory.create(application_role=application_role)

    # create role for environment in a different app in same portfolio
    application = ApplicationFactory.create(portfolio=portfolio)
    env_role_3 = EnvironmentRoleFactory.create(
        application_role=ApplicationRoleFactory.create(
            application=application, user=user
        )
    )

    # create role for environment for random user in app2
    rando_app_role = ApplicationRoleFactory.create(application=application)
    rando_env_role = EnvironmentRoleFactory.create(application_role=rando_app_role)

    env_roles = EnvironmentRoles.for_user(user.id, portfolio.id)
    assert len(env_roles) == 3
    assert env_roles == [env_role_1, env_role_2, env_role_3]
    assert not rando_env_role in env_roles


class TestPendingCreation:
    def test_pending_role(self):
        appr = ApplicationRoleFactory.create(cloud_id="123")
        envr = EnvironmentRoleFactory.create(application_role=appr)
        assert EnvironmentRoles.get_pending_creation() == [envr.id]

    def test_deleted_role(self):
        appr = ApplicationRoleFactory.create(cloud_id="123")
        envr = EnvironmentRoleFactory.create(application_role=appr, deleted=True)
        assert EnvironmentRoles.get_pending_creation() == []

    def test_not_ready_role(self):
        appr = ApplicationRoleFactory.create(cloud_id=None)
        envr = EnvironmentRoleFactory.create(application_role=appr)
        assert EnvironmentRoles.get_pending_creation() == []

    def test_disabled_app_role(self):
        appr = ApplicationRoleFactory.create(
            cloud_id="123", status=ApplicationRoleStatus.DISABLED
        )
        envr = EnvironmentRoleFactory.create(application_role=appr)
        assert EnvironmentRoles.get_pending_creation() == []

    def test_disabled_env_role(self):
        appr = ApplicationRoleFactory.create(cloud_id="123")
        envr = EnvironmentRoleFactory.create(
            application_role=appr, status=EnvironmentRole.Status.DISABLED
        )
        assert EnvironmentRoles.get_pending_creation() == []
