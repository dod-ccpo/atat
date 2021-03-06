from uuid import uuid4

import pytest

from atat.domain.environment_roles import EnvironmentRoles
from atat.domain.environments import Environments
from atat.domain.exceptions import AlreadyExistsError, DisabledError, NotFoundError
from atat.models.environment_role import CSPRole
from tests.factories import (
    ApplicationFactory,
    ApplicationRoleFactory,
    EnvironmentFactory,
    EnvironmentRoleFactory,
)
from tests.utils import EnvQueryTest


def test_create_environments():
    application = ApplicationFactory.create()
    environments = Environments.create_many(
        application.portfolio.owner, application, ["Staging", "Production"]
    )
    for env in environments:
        assert env.cloud_id is None


def test_update_env_role():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.ADMIN)
    new_role = CSPRole.BILLING_READ
    Environments.update_env_role(
        env_role.environment, env_role.application_role, new_role
    )
    assert env_role.role == new_role


def test_update_env_role_no_access():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.ADMIN)
    Environments.update_env_role(env_role.environment, env_role.application_role, None)

    assert not EnvironmentRoles.get(
        env_role.application_role.id, env_role.environment.id
    )
    assert env_role.role is None
    assert env_role.is_disabled


def test_update_env_role_disabled_role():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.ADMIN)
    Environments.update_env_role(env_role.environment, env_role.application_role, None)

    # An exception should be raised when a new role is passed to Environments.update_env_role
    with pytest.raises(DisabledError):
        Environments.update_env_role(
            env_role.environment,
            env_role.application_role,
            CSPRole.BILLING_READ,
        )

    assert env_role.role is None
    assert env_role.is_disabled

    # An exception should not be raised when no new role is passed
    Environments.update_env_role(env_role.environment, env_role.application_role, None)


def test_get_excludes_deleted():
    env = EnvironmentFactory.create(
        deleted=True, application=ApplicationFactory.create()
    )
    with pytest.raises(NotFoundError):
        Environments.get(env.id)


def test_delete_environment(session):
    env = EnvironmentFactory.create(application=ApplicationFactory.create())
    env_role = EnvironmentRoleFactory.create(
        application_role=ApplicationRoleFactory.create(application=env.application),
        environment=env,
    )
    assert not env.deleted
    assert not env_role.deleted
    Environments.delete(env)
    assert env.deleted
    assert env_role.deleted
    # did not flush
    assert session.dirty

    Environments.delete(env, commit=True)
    assert env.deleted
    assert env_role.deleted
    # flushed the change
    assert not session.dirty


def test_update_environment():
    environment = EnvironmentFactory.create()
    assert environment.name is not "name 2"
    Environments.update(environment, new_data={"name": "name 2"})
    assert environment.name == "name 2"


def test_create_does_not_duplicate_names_within_application():
    application = ApplicationFactory.create()
    name = "Your Environment"
    user = application.portfolio.owner

    assert Environments.create(user, application, name)
    with pytest.raises(AlreadyExistsError):
        Environments.create(user, application, name)


def test_update_does_not_duplicate_names_within_application():
    application = ApplicationFactory.create()
    name = "Your Environment"
    EnvironmentFactory.create(application=application, name=name)
    dupe_env = EnvironmentFactory.create(application=application)

    with pytest.raises(AlreadyExistsError):
        Environments.update(dupe_env, new_data={"name": name})


class TestGetEnvironmentsPendingCreate(EnvQueryTest):
    def test_with_expired_clins(self, session):
        self.create_portfolio_with_clins([(self.YESTERDAY, self.YESTERDAY)])
        assert len(Environments.get_environments_pending_creation(self.NOW)) == 0

    def test_with_active_clin(self, session):
        portfolio = self.create_portfolio_with_clins([(self.YESTERDAY, self.TOMORROW)])
        Environments.get_environments_pending_creation(self.NOW) == [
            portfolio.applications[0].environments[0].id
        ]

    def test_with_future_clin(self, session):
        self.create_portfolio_with_clins([(self.TOMORROW, self.TOMORROW)])
        assert len(Environments.get_environments_pending_creation(self.NOW)) == 0

    def test_with_already_provisioned_app(self, session):
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.TOMORROW)], app_data={"cloud_id": uuid4().hex}
        )
        assert len(Environments.get_environments_pending_creation(self.NOW)) == 1

    def test_apps_and_envs_with_and_without_cloud_id(self, session):
        """This test creates a variety of applications and environments, but for
        each combination, they are created such that no environment ids should
        be returned by the query."""

        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.TOMORROW), (self.YESTERDAY, self.TOMORROW)],
            app_data={"cloud_id": uuid4().hex},
            env_data={"cloud_id": uuid4().hex},
        )
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.TOMORROW), (self.YESTERDAY, self.TOMORROW)],
        )
        assert len(Environments.get_environments_pending_creation(self.NOW)) == 0

    def test_with_already_provisioned_env(self, session):
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.TOMORROW)],
            env_data={"cloud_id": uuid4().hex},
            app_data={"cloud_id": uuid4().hex},
        )

    def test_with_multiple_active_CLINs(self, session):
        self.create_portfolio_with_clins(
            [
                (self.YESTERDAY, self.TOMORROW),
                (self.YESTERDAY, self.TOMORROW),
                (self.YESTERDAY, self.TOMORROW),
            ],
            app_data={"cloud_id": uuid4().hex},
            env_data={"cloud_id": None},
        )
        envs_pending_creation = Environments.get_environments_pending_creation(self.NOW)
        assert len(envs_pending_creation) == 1


def test_create_many_environments_will_skip_already_created_names():
    application = ApplicationFactory.create()
    Environments.create_many(
        application.portfolio.owner, application, ["Staging", "Production"]
    )
    Environments.create_many(
        application.portfolio.owner,
        application,
        ["Staging", "Production", "Development"],
    )
    assert len(application.environments) == 3
