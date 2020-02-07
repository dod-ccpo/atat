import pendulum
import pytest
from uuid import uuid4
from unittest.mock import Mock
from smtplib import SMTPException
from azure.core.exceptions import AzureError

from atst.domain.csp.cloud import MockCloudProvider
from atst.domain.portfolios import Portfolios
from atst.models import ApplicationRoleStatus

from atst.jobs import (
    RecordFailure,
    dispatch_create_environment,
    dispatch_create_application,
    dispatch_create_user,
    dispatch_provision_portfolio,
    dispatch_send_task_order_files,
    create_environment,
    do_create_user,
    do_provision_portfolio,
    do_create_environment,
    do_create_application,
)
from tests.factories import (
    ApplicationFactory,
    ApplicationRoleFactory,
    EnvironmentFactory,
    EnvironmentRoleFactory,
    PortfolioFactory,
    PortfolioStateMachineFactory,
    TaskOrderFactory,
    UserFactory,
)
from atst.models import CSPRole, EnvironmentRole, ApplicationRoleStatus, JobFailure
from atst.utils.localization import translate


@pytest.fixture(autouse=True, scope="function")
def csp():
    return Mock(wraps=MockCloudProvider({}, with_delay=False, with_failure=False))


@pytest.fixture(scope="function")
def portfolio():
    portfolio = PortfolioFactory.create()
    return portfolio


def _find_failure(session, entity, id_):
    return (
        session.query(JobFailure)
        .filter(JobFailure.entity == entity)
        .filter(JobFailure.entity_id == id_)
        .one()
    )


def test_environment_job_failure(session, celery_app, celery_worker):
    @celery_app.task(bind=True, base=RecordFailure)
    def _fail_hard(self, environment_id=None):
        raise ValueError("something bad happened")

    environment = EnvironmentFactory.create()
    celery_worker.reload()

    # Use apply instead of delay since we are testing the on_failure hook only
    task = _fail_hard.apply(kwargs={"environment_id": environment.id})
    with pytest.raises(ValueError):
        task.get()

    job_failure = _find_failure(session, "environment", str(environment.id))
    assert job_failure.task == task


def test_environment_role_job_failure(session, celery_app, celery_worker):
    @celery_app.task(bind=True, base=RecordFailure)
    def _fail_hard(self, environment_role_id=None):
        raise ValueError("something bad happened")

    role = EnvironmentRoleFactory.create()
    celery_worker.reload()

    # Use apply instead of delay since we are testing the on_failure hook only
    task = _fail_hard.apply(kwargs={"environment_role_id": role.id})
    with pytest.raises(ValueError):
        task.get()

    job_failure = _find_failure(session, "environment_role", str(role.id))
    assert job_failure.task == task


now = pendulum.now()
yesterday = now.subtract(days=1)
tomorrow = now.add(days=1)


def test_create_environment_job(session, csp):
    environment = EnvironmentFactory.create()
    environment.application.cloud_id = "parentId"
    environment.application.portfolio.csp_data = {"tenant_id": "fake"}
    session.add(environment)
    session.commit()
    do_create_environment(csp, environment.id)
    session.refresh(environment)

    assert environment.cloud_id


def test_create_environment_job_is_idempotent(csp, session):
    environment = EnvironmentFactory.create(cloud_id=uuid4().hex)
    do_create_environment(csp, environment.id)

    csp.create_environment.assert_not_called()


def test_create_application_job(session, csp):
    portfolio = PortfolioFactory.create(
        csp_data={"tenant_id": str(uuid4()), "root_management_group_id": str(uuid4())}
    )
    application = ApplicationFactory.create(portfolio=portfolio, cloud_id=None)
    do_create_application(csp, application.id)
    session.refresh(application)

    assert application.cloud_id


def test_create_application_job_is_idempotent(csp):
    application = ApplicationFactory.create(cloud_id=uuid4())
    do_create_application(csp, application.id)

    csp.create_application.assert_not_called()


def test_create_user_job(session, csp):
    portfolio = PortfolioFactory.create(
        csp_data={
            "tenant_id": str(uuid4()),
            "domain_name": "rebelalliance.onmicrosoft.com",
        }
    )
    application = ApplicationFactory.create(portfolio=portfolio, cloud_id="321")
    user = UserFactory.create(
        first_name="Han", last_name="Solo", email="han@example.com"
    )
    app_role = ApplicationRoleFactory.create(
        application=application,
        user=user,
        status=ApplicationRoleStatus.ACTIVE,
        cloud_id=None,
    )

    do_create_user(csp, [app_role.id])
    session.refresh(app_role)

    assert app_role.cloud_id


def test_dispatch_create_environment(session, monkeypatch):
    # Given that I have a portfolio with an active CLIN and two environments,
    # one of which is deleted
    portfolio = PortfolioFactory.create(
        applications=[{"environments": [{}, {}], "cloud_id": uuid4().hex}],
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


def test_dispatch_create_application(monkeypatch):
    portfolio = PortfolioFactory.create(state="COMPLETED")
    app = ApplicationFactory.create(portfolio=portfolio)

    mock = Mock()
    monkeypatch.setattr("atst.jobs.create_application", mock)

    # When dispatch_create_application is called
    dispatch_create_application.run()

    # It should cause the create_application task to be called once
    # with the application id
    mock.delay.assert_called_once_with(application_id=app.id)


def test_dispatch_create_user(monkeypatch):
    application = ApplicationFactory.create(cloud_id="123")
    user = UserFactory.create(
        first_name="Han", last_name="Solo", email="han@example.com"
    )
    app_role = ApplicationRoleFactory.create(
        application=application,
        user=user,
        status=ApplicationRoleStatus.ACTIVE,
        cloud_id=None,
    )

    mock = Mock()
    monkeypatch.setattr("atst.jobs.create_user", mock)

    # When dispatch_create_user is called
    dispatch_create_user.run()

    # It should cause the create_user task to be called once
    # with the application id
    mock.delay.assert_called_once_with(application_role_ids=[app_role.id])


def test_create_environment_no_dupes(session, celery_app, celery_worker):
    portfolio = PortfolioFactory.create(
        applications=[{"environments": [{"cloud_id": uuid4().hex}]}],
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


def test_dispatch_provision_portfolio(csp, monkeypatch):
    portfolio = PortfolioFactory.create(
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
    sm = PortfolioStateMachineFactory.create(portfolio=portfolio)
    mock = Mock()
    monkeypatch.setattr("atst.jobs.provision_portfolio", mock)
    dispatch_provision_portfolio.run()
    mock.delay.assert_called_once_with(portfolio_id=portfolio.id)


def test_do_provision_portfolio(csp, session, portfolio):
    do_provision_portfolio(csp=csp, portfolio_id=portfolio.id)
    session.refresh(portfolio)
    assert portfolio.state_machine


def test_provision_portfolio_create_tenant(
    csp, session, portfolio, celery_app, celery_worker, monkeypatch
):
    sm = PortfolioStateMachineFactory.create(portfolio=portfolio)
    # mock = Mock()
    # monkeypatch.setattr("atst.jobs.provision_portfolio", mock)
    # dispatch_provision_portfolio.run()
    # mock.delay.assert_called_once_with(portfolio_id=portfolio.id)


# TODO: Refactor the tests related to dispatch_send_task_order_files() into a class
# and separate the success test into two tests
def test_dispatch_send_task_order_files(monkeypatch, app):
    mock = Mock()
    monkeypatch.setattr("atst.jobs.send_mail", mock)

    def _download_task_order(MockFileService, object_name):
        return {"name": object_name}

    monkeypatch.setattr(
        "atst.domain.csp.files.MockFileService.download_task_order",
        _download_task_order,
    )

    # Create 3 new Task Orders
    for i in range(3):
        TaskOrderFactory.create(create_clins=[{"number": "0001"}])

    dispatch_send_task_order_files.run()

    # Check that send_with_attachment was called once for each task order
    assert mock.call_count == 3
    mock.reset_mock()

    # Create new TO
    task_order = TaskOrderFactory.create(create_clins=[{"number": "0001"}])
    assert not task_order.pdf_last_sent_at

    dispatch_send_task_order_files.run()

    # Check that send_with_attachment was called with correct kwargs
    mock.assert_called_once_with(
        recipients=[app.config.get("MICROSOFT_TASK_ORDER_EMAIL_ADDRESS")],
        subject=translate(
            "email.task_order_sent.subject", {"to_number": task_order.number}
        ),
        body=translate("email.task_order_sent.body", {"to_number": task_order.number}),
        attachments=[
            {
                "name": task_order.pdf.object_name,
                "maintype": "application",
                "subtype": "pdf",
            }
        ],
    )

    assert task_order.pdf_last_sent_at


def test_dispatch_send_task_order_files_send_failure(monkeypatch):
    def _raise_smtp_exception(**kwargs):
        raise SMTPException

    monkeypatch.setattr("atst.jobs.send_mail", _raise_smtp_exception)

    task_order = TaskOrderFactory.create(create_clins=[{"number": "0001"}])
    dispatch_send_task_order_files.run()

    # Check that pdf_last_sent_at has not been updated
    assert not task_order.pdf_last_sent_at


def test_dispatch_send_task_order_files_download_failure(monkeypatch):
    mock = Mock()
    monkeypatch.setattr("atst.jobs.send_mail", mock)

    def _download_task_order(MockFileService, object_name):
        raise AzureError("something went wrong")

    monkeypatch.setattr(
        "atst.domain.csp.files.MockFileService.download_task_order",
        _download_task_order,
    )

    task_order = TaskOrderFactory.create(create_clins=[{"number": "0002"}])
    dispatch_send_task_order_files.run()

    # Check that pdf_last_sent_at has not been updated
    assert not task_order.pdf_last_sent_at
