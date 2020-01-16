import pendulum
import pytest
from uuid import uuid4
from unittest.mock import Mock
from threading import Thread

from atst.domain.csp.cloud import MockCloudProvider
from atst.jobs import (
    RecordEnvironmentFailure,
    RecordEnvironmentRoleFailure,
    do_create_environment,
    do_create_atat_admin_user,
    dispatch_create_environment,
    dispatch_create_atat_admin_user,
    create_environment,
    dispatch_provision_user,
    do_provision_user,
)
from atst.models.utils import claim_for_update
from atst.domain.exceptions import ClaimFailedException
from tests.factories import (
    EnvironmentFactory,
    EnvironmentRoleFactory,
    PortfolioFactory,
    ApplicationRoleFactory,
)
from atst.models import EnvironmentRole, ApplicationRoleStatus


@pytest.fixture(autouse=True, scope="function")
def csp():
    return Mock(wraps=MockCloudProvider({}, with_delay=False, with_failure=False))


def test_environment_job_failure(celery_app, celery_worker):
    @celery_app.task(bind=True, base=RecordEnvironmentFailure)
    def _fail_hard(self, environment_id=None):
        raise ValueError("something bad happened")

    environment = EnvironmentFactory.create()
    celery_worker.reload()

    # Use apply instead of delay since we are testing the on_failure hook only
    task = _fail_hard.apply(kwargs={"environment_id": environment.id})
    with pytest.raises(ValueError):
        task.get()

    assert environment.job_failures
    job_failure = environment.job_failures[0]
    assert job_failure.task == task


def test_environment_role_job_failure(celery_app, celery_worker):
    @celery_app.task(bind=True, base=RecordEnvironmentRoleFailure)
    def _fail_hard(self, environment_role_id=None):
        raise ValueError("something bad happened")

    role = EnvironmentRoleFactory.create()
    celery_worker.reload()

    # Use apply instead of delay since we are testing the on_failure hook only
    task = _fail_hard.apply(kwargs={"environment_role_id": role.id})
    with pytest.raises(ValueError):
        task.get()

    assert role.job_failures
    job_failure = role.job_failures[0]
    assert job_failure.task == task


now = pendulum.now()
yesterday = now.subtract(days=1)
tomorrow = now.add(days=1)


def test_create_environment_job(session, csp):
    environment = EnvironmentFactory.create()
    do_create_environment(csp, environment.id)
    session.refresh(environment)

    assert environment.cloud_id


def test_create_environment_job_is_idempotent(csp, session):
    environment = EnvironmentFactory.create(cloud_id=uuid4().hex)
    do_create_environment(csp, environment.id)

    csp.create_environment.assert_not_called()


def test_create_atat_admin_user(csp, session):
    environment = EnvironmentFactory.create(cloud_id="something")
    do_create_atat_admin_user(csp, environment.id)
    session.refresh(environment)

    assert environment.root_user_info


def test_dispatch_create_environment(session, monkeypatch):
    # Given that I have a portfolio with an active CLIN and two environments,
    # one of which is deleted
    portfolio = PortfolioFactory.create(
        applications=[{"environments": [{}, {}]}],
        task_orders=[
            {
                "create_clins": [
                    {
                        "start_date": pendulum.now().subtract(days=1),
                        "end_date": pendulum.now().add(days=1),
                    }
                ]
            }
        ],
    )
    [e1, e2] = portfolio.applications[0].environments
    e2.deleted = True
    session.add(e2)
    session.commit()

    mock = Mock()
    monkeypatch.setattr("atst.jobs.create_environment", mock)

    # When dispatch_create_environment is called
    dispatch_create_environment.run()

    # It should cause the create_environment task to be called once with the
    # non-deleted environment
    mock.delay.assert_called_once_with(environment_id=e1.id)


def test_dispatch_create_atat_admin_user(session, monkeypatch):
    portfolio = PortfolioFactory.create(
        applications=[
            {"environments": [{"cloud_id": uuid4().hex, "root_user_info": None}]}
        ],
        task_orders=[
            {
                "create_clins": [
                    {
                        "start_date": pendulum.now().subtract(days=1),
                        "end_date": pendulum.now().add(days=1),
                    }
                ]
            }
        ],
    )
    mock = Mock()
    monkeypatch.setattr("atst.jobs.create_atat_admin_user", mock)
    environment = portfolio.applications[0].environments[0]

    dispatch_create_atat_admin_user.run()

    mock.delay.assert_called_once_with(environment_id=environment.id)


def test_create_environment_no_dupes(session, celery_app, celery_worker):
    portfolio = PortfolioFactory.create(
        applications=[
            {"environments": [{"cloud_id": uuid4().hex, "root_user_info": {}}]}
        ],
        task_orders=[
            {
                "create_clins": [
                    {
                        "start_date": pendulum.now().subtract(days=1),
                        "end_date": pendulum.now().add(days=1),
                    }
                ]
            }
        ],
    )
    environment = portfolio.applications[0].environments[0]

    # create_environment is run twice on the same environment
    create_environment.run(environment_id=environment.id)
    session.refresh(environment)

    first_cloud_id = environment.cloud_id

    create_environment.run(environment_id=environment.id)
    session.refresh(environment)

    # The environment's cloud_id was not overwritten in the second run
    assert environment.cloud_id == first_cloud_id

    # The environment's claim was released
    assert environment.claimed_until == None


def test_claim_for_update(session):
    portfolio = PortfolioFactory.create(
        applications=[
            {"environments": [{"cloud_id": uuid4().hex, "root_user_info": {}}]}
        ],
        task_orders=[
            {
                "create_clins": [
                    {
                        "start_date": pendulum.now().subtract(days=1),
                        "end_date": pendulum.now().add(days=1),
                    }
                ]
            }
        ],
    )
    environment = portfolio.applications[0].environments[0]

    satisfied_claims = []
    exceptions = []

    # Two threads race to do work on environment and check out the lock
    class FirstThread(Thread):
        def run(self):
            try:
                with claim_for_update(environment):
                    satisfied_claims.append("FirstThread")
            except ClaimFailedException:
                exceptions.append("FirstThread")

    class SecondThread(Thread):
        def run(self):
            try:
                with claim_for_update(environment):
                    satisfied_claims.append("SecondThread")
            except ClaimFailedException:
                exceptions.append("SecondThread")

    t1 = FirstThread()
    t2 = SecondThread()
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    session.refresh(environment)

    assert len(satisfied_claims) == 1
    assert len(exceptions) == 1

    if satisfied_claims == ["FirstThread"]:
        assert exceptions == ["SecondThread"]
    else:
        assert satisfied_claims == ["SecondThread"]
        assert exceptions == ["FirstThread"]

    # The claim is released
    assert environment.claimed_until is None


def test_dispatch_provision_user(csp, session, celery_app, celery_worker, monkeypatch):
    # Given that I have four environment roles:
    #   (A) one of which has a completed status
    #   (B) one of which has an environment that has not been provisioned
    #   (C) one of which is pending, has a provisioned environment but an inactive application role
    #   (D) one of which is pending, has a provisioned environment and has an active application role
    provisioned_environment = EnvironmentFactory.create(
        cloud_id="cloud_id", root_user_info={}
    )
    unprovisioned_environment = EnvironmentFactory.create()
    _er_a = EnvironmentRoleFactory.create(
        environment=provisioned_environment, status=EnvironmentRole.Status.COMPLETED
    )
    _er_b = EnvironmentRoleFactory.create(
        environment=unprovisioned_environment, status=EnvironmentRole.Status.PENDING
    )
    _er_c = EnvironmentRoleFactory.create(
        environment=unprovisioned_environment,
        status=EnvironmentRole.Status.PENDING,
        application_role=ApplicationRoleFactory(status=ApplicationRoleStatus.PENDING),
    )
    er_d = EnvironmentRoleFactory.create(
        environment=provisioned_environment,
        status=EnvironmentRole.Status.PENDING,
        application_role=ApplicationRoleFactory(status=ApplicationRoleStatus.ACTIVE),
    )

    mock = Mock()
    monkeypatch.setattr("atst.jobs.provision_user", mock)

    # When I dispatch the user provisioning task
    dispatch_provision_user.run()

    # I expect it to dispatch only one call, to EnvironmentRole D
    mock.delay.assert_called_once_with(environment_role_id=er_d.id)


def test_do_provision_user(csp, session):
    # Given that I have an EnvironmentRole with a provisioned environment
    credentials = MockCloudProvider(())._auth_credentials
    provisioned_environment = EnvironmentFactory.create(
        cloud_id="cloud_id", root_user_info={"credentials": credentials}
    )
    environment_role = EnvironmentRoleFactory.create(
        environment=provisioned_environment,
        status=EnvironmentRole.Status.PENDING,
        role="my_role",
    )

    # When I call the user provisoning task
    do_provision_user(csp=csp, environment_role_id=environment_role.id)

    session.refresh(environment_role)
    # I expect that the CSP create_or_update_user method will be called
    csp.create_or_update_user.assert_called_once_with(
        credentials, environment_role, "my_role"
    )
    # I expect that the EnvironmentRole now has a csp_user_id
    assert environment_role.csp_user_id
