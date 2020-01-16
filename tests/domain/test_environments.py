import pytest
import pendulum
from uuid import uuid4

from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.exceptions import AlreadyExistsError, DisabledError, NotFoundError
from atst.models.environment_role import CSPRole, EnvironmentRole

from tests.factories import (
    ApplicationFactory,
    PortfolioFactory,
    EnvironmentFactory,
    EnvironmentRoleFactory,
    ApplicationRoleFactory,
)


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
    assert env_role.disabled


def test_update_env_role_disabled_role():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.ADMIN)
    Environments.update_env_role(env_role.environment, env_role.application_role, None)

    # An exception should be raised when a new role is passed to Environments.update_env_role
    with pytest.raises(DisabledError):
        Environments.update_env_role(
            env_role.environment, env_role.application_role, CSPRole.BILLING_READ,
        )

    assert env_role.role is None
    assert env_role.disabled

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
    Environments.update(environment, name="name 2")
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
    environment = EnvironmentFactory.create(application=application, name=name)
    dupe_env = EnvironmentFactory.create(application=application)
    user = application.portfolio.owner

    with pytest.raises(AlreadyExistsError):
        Environments.update(dupe_env, name)


class EnvQueryTest:
    @property
    def NOW(self):
        return pendulum.now()

    @property
    def YESTERDAY(self):
        return self.NOW.subtract(days=1)

    @property
    def TOMORROW(self):
        return self.NOW.add(days=1)

    def create_portfolio_with_clins(self, start_and_end_dates, env_data=None):
        env_data = env_data or {}
        return PortfolioFactory.create(
            applications=[
                {
                    "name": "Mos Eisley",
                    "description": "Where Han shot first",
                    "environments": [{"name": "thebar", **env_data}],
                }
            ],
            task_orders=[
                {
                    "create_clins": [
                        {"start_date": start_date, "end_date": end_date}
                        for (start_date, end_date) in start_and_end_dates
                    ]
                }
            ],
        )


class TestGetEnvironmentsPendingCreate(EnvQueryTest):
    def test_with_expired_clins(self, session):
        self.create_portfolio_with_clins([(self.YESTERDAY, self.YESTERDAY)])
        assert len(Environments.get_environments_pending_creation(self.NOW)) == 0

    def test_with_active_clins(self, session):
        portfolio = self.create_portfolio_with_clins([(self.YESTERDAY, self.TOMORROW)])
        Environments.get_environments_pending_creation(self.NOW) == [
            portfolio.applications[0].environments[0].id
        ]

    def test_with_future_clins(self, session):
        self.create_portfolio_with_clins([(self.TOMORROW, self.TOMORROW)])
        assert len(Environments.get_environments_pending_creation(self.NOW)) == 0

    def test_with_already_provisioned_env(self, session):
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.TOMORROW)], env_data={"cloud_id": uuid4().hex}
        )
        assert len(Environments.get_environments_pending_creation(self.NOW)) == 0


class TestGetEnvironmentsPendingAtatUserCreation(EnvQueryTest):
    def test_with_provisioned_environment(self):
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.TOMORROW)],
            {"cloud_id": uuid4().hex, "root_user_info": {}},
        )
        assert (
            len(Environments.get_environments_pending_atat_user_creation(self.NOW)) == 0
        )

    def test_with_unprovisioned_environment(self):
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.TOMORROW)],
            {"cloud_id": uuid4().hex, "root_user_info": None},
        )
        assert (
            len(Environments.get_environments_pending_atat_user_creation(self.NOW)) == 1
        )

    def test_with_unprovisioned_expired_clins_environment(self):
        self.create_portfolio_with_clins(
            [(self.YESTERDAY, self.YESTERDAY)],
            {"cloud_id": uuid4().hex, "root_user_info": None},
        )
        assert (
            len(Environments.get_environments_pending_atat_user_creation(self.NOW)) == 0
        )
