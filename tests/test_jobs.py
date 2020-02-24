import pendulum
import pytest
from uuid import uuid4
from unittest.mock import Mock, MagicMock
from smtplib import SMTPException
from azure.core.exceptions import AzureError

from atat.domain.csp.cloud import MockCloudProvider
from atat.domain.csp.cloud.models import BillingInstructionCSPPayload, UserRoleCSPResult
from atat.domain.portfolios import Portfolios
from atat.models import ApplicationRoleStatus, Portfolio, FSMStates

from atat.jobs import (
    RecordFailure,
    dispatch_create_environment,
    dispatch_create_application,
    dispatch_create_user,
    dispatch_create_environment_role,
    dispatch_provision_portfolio,
    create_billing_instruction,
    create_environment,
    do_create_user,
    do_provision_portfolio,
    do_create_environment,
    do_create_environment_role,
    do_create_application,
    send_PPOC_email,
    send_task_order_files,
)
from tests.factories import (
    ApplicationFactory,
    ApplicationRoleFactory,
    CLINFactory,
    EnvironmentFactory,
    EnvironmentRoleFactory,
    PortfolioFactory,
    PortfolioStateMachineFactory,
    TaskOrderFactory,
    UserFactory,
)
from atat.models import CSPRole, EnvironmentRole, ApplicationRoleStatus, JobFailure
from atat.utils.localization import translate


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
    environment.portfolio.csp_data = {"tenant_id": "fake"}
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


class TestCreateUserJob:
    @pytest.fixture
    def portfolio(self, app):
        return PortfolioFactory.create(
            csp_data={
                "tenant_id": str(uuid4()),
                "domain_name": f"rebelalliance.{app.config.get('OFFICE_365_DOMAIN')}",
            }
        )

    @pytest.fixture
    def app_1(self, portfolio):
        return ApplicationFactory.create(portfolio=portfolio, cloud_id="321")

    @pytest.fixture
    def app_2(self, portfolio):
        return ApplicationFactory.create(portfolio=portfolio, cloud_id="123")

    @pytest.fixture
    def user(self):
        return UserFactory.create(
            first_name="Han", last_name="Solo", email="han@example.com"
        )

    @pytest.fixture
    def app_role_1(self, app_1, user):
        return ApplicationRoleFactory.create(
            application=app_1,
            user=user,
            status=ApplicationRoleStatus.ACTIVE,
            cloud_id=None,
        )

    @pytest.fixture
    def app_role_2(self, app_2, user):
        return ApplicationRoleFactory.create(
            application=app_2,
            user=user,
            status=ApplicationRoleStatus.ACTIVE,
            cloud_id=None,
        )

    def test_create_user_job(self, session, csp, app_role_1):
        assert not app_role_1.cloud_id

        session.begin_nested()
        do_create_user(csp, [app_role_1.id])
        session.rollback()

        assert app_role_1.cloud_id

    def test_create_user_sends_email(self, monkeypatch, csp, app_role_1, app_role_2):
        mock = Mock()
        monkeypatch.setattr("atat.jobs.send_mail", mock)

        do_create_user(csp, [app_role_1.id, app_role_2.id])
        assert mock.call_count == 1


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
    monkeypatch.setattr("atat.jobs.create_environment", mock)

    # When dispatch_create_environment is called
    dispatch_create_environment.run()

    # It should cause the create_environment task to be called once with the
    # non-deleted environment
    mock.delay.assert_called_once_with(environment_id=e1.id)


def test_dispatch_create_application(monkeypatch):
    portfolio = PortfolioFactory.create(state="COMPLETED")
    app = ApplicationFactory.create(portfolio=portfolio)

    mock = Mock()
    monkeypatch.setattr("atat.jobs.create_application", mock)

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
    monkeypatch.setattr("atat.jobs.create_user", mock)

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
    monkeypatch.setattr("atat.jobs.provision_portfolio", mock)
    dispatch_provision_portfolio.run()
    mock.delay.assert_called_once_with(portfolio_id=portfolio.id)


class TestDoProvisionPortfolio:
    def test_portfolio_has_state_machine(self, csp, session, portfolio):
        do_provision_portfolio(csp=csp, portfolio_id=portfolio.id)
        session.refresh(portfolio)
        assert portfolio.state_machine

    def test_sends_email_to_PPOC_on_completion(
        self, monkeypatch, csp, portfolio: Portfolio
    ):
        mock = Mock()
        monkeypatch.setattr("atat.jobs.send_PPOC_email", mock)

        csp._authorize.return_value = None
        csp._maybe_raise.return_value = None
        sm: PortfolioStateMachine = PortfolioStateMachineFactory.create(
            portfolio=portfolio
        )
        # The stage before "COMPLETED"
        sm.state = FSMStates.BILLING_OWNER_CREATED
        do_provision_portfolio(csp=csp, portfolio_id=portfolio.id)

        # send_PPOC_email was called
        assert mock.assert_called_once


def test_send_ppoc_email(monkeypatch, app):
    mock = Mock()
    monkeypatch.setattr("atat.jobs.send_mail", mock)

    ppoc_email = "example@example.com"
    user_id = "user_id"
    domain_name = "domain"

    send_PPOC_email(
        {
            "password_recovery_email_address": ppoc_email,
            "user_id": user_id,
            "domain_name": domain_name,
        }
    )
    mock.assert_called_once_with(
        recipients=[ppoc_email],
        subject=translate("email.portfolio_ready.subject"),
        body=translate(
            "email.portfolio_ready.body",
            {
                "password_reset_address": app.config.get("AZURE_LOGIN_URL"),
                "username": f"{user_id}@{domain_name}.{app.config.get('OFFICE_365_DOMAIN')}",
            },
        ),
    )


def test_provision_portfolio_create_tenant(
    csp, session, portfolio, celery_app, celery_worker, monkeypatch
):
    sm = PortfolioStateMachineFactory.create(portfolio=portfolio)
    # mock = Mock()
    # monkeypatch.setattr("atat.jobs.provision_portfolio", mock)
    # dispatch_provision_portfolio.run()
    # mock.delay.assert_called_once_with(portfolio_id=portfolio.id)


def test_dispatch_create_environment_role(monkeypatch):
    portfolio = PortfolioFactory.create(csp_data={"tenant_id": "123"})
    app_role = ApplicationRoleFactory.create(
        application=ApplicationFactory.create(portfolio=portfolio),
        status=ApplicationRoleStatus.ACTIVE,
        cloud_id="123",
    )
    env_role = EnvironmentRoleFactory.create(application_role=app_role)

    mock = Mock()
    monkeypatch.setattr("atat.jobs.create_environment_role", mock)

    dispatch_create_environment_role.run()

    mock.delay.assert_called_once_with(environment_role_id=env_role.id)


class TestCreateEnvironmentRole:
    @pytest.fixture
    def env_role(self):
        portfolio = PortfolioFactory.create(csp_data={"tenant_id": "123"})
        app = ApplicationFactory.create(portfolio=portfolio)
        app_role = ApplicationRoleFactory.create(
            application=app, status=ApplicationRoleStatus.ACTIVE, cloud_id="123",
        )
        env = EnvironmentFactory.create(application=app, cloud_id="123")
        return EnvironmentRoleFactory.create(
            environment=env, application_role=app_role, cloud_id=None
        )

    @pytest.fixture
    def csp(self):
        csp = Mock()
        result = UserRoleCSPResult(id="a-cloud-id")
        csp.create_user_role = MagicMock(return_value=result)
        return csp

    def test_success(self, env_role, csp):
        do_create_environment_role(csp, environment_role_id=env_role.id)
        assert env_role.cloud_id == "a-cloud-id"

    def test_sends_email(self, monkeypatch, env_role, csp):
        send_mail = Mock()
        monkeypatch.setattr("atat.jobs.send_mail", send_mail)
        do_create_environment_role(csp, environment_role_id=env_role.id)
        assert send_mail.call_count == 1


class TestSendTaskOrderFiles:
    @pytest.fixture(scope="function")
    def send_mail(self, monkeypatch):
        mock = Mock()
        monkeypatch.setattr("atat.jobs.send_mail", mock)
        return mock

    @pytest.fixture(scope="function")
    def download_task_order(self, monkeypatch):
        def _download_task_order(MockFileService, object_name):
            return {"name": object_name}

        monkeypatch.setattr(
            "atat.domain.csp.files.MockFileService.download_task_order",
            _download_task_order,
        )

    def test_sends_multiple_emails(self, send_mail, download_task_order):
        # Create 3 Task Orders
        for i in range(3):
            TaskOrderFactory.create(create_clins=[{"number": "0001"}])

        send_task_order_files.run()

        # Check that send_with_attachment was called once for each task order
        assert send_mail.call_count == 3

    def test_kwargs(self, send_mail, download_task_order, app):
        task_order = TaskOrderFactory.create(create_clins=[{"number": "0001"}])
        send_task_order_files.run()

        # Check that send_with_attachment was called with correct kwargs
        send_mail.assert_called_once_with(
            recipients=[app.config.get("MICROSOFT_TASK_ORDER_EMAIL_ADDRESS")],
            subject=translate(
                "email.task_order_sent.subject", {"to_number": task_order.number}
            ),
            body=translate(
                "email.task_order_sent.body", {"to_number": task_order.number}
            ),
            attachments=[
                {
                    "name": task_order.pdf.object_name,
                    "maintype": "application",
                    "subtype": "pdf",
                }
            ],
        )
        assert task_order.pdf_last_sent_at

    def test_send_failure(self, monkeypatch):
        def _raise_smtp_exception(**kwargs):
            raise SMTPException

        monkeypatch.setattr("atat.jobs.send_mail", _raise_smtp_exception)
        task_order = TaskOrderFactory.create(create_clins=[{"number": "0001"}])
        send_task_order_files.run()

        # Check that pdf_last_sent_at has not been updated
        assert not task_order.pdf_last_sent_at

    def test_download_failure(self, send_mail, monkeypatch):
        def _download_task_order(MockFileService, object_name):
            raise AzureError("something went wrong")

        monkeypatch.setattr(
            "atat.domain.csp.files.MockFileService.download_task_order",
            _download_task_order,
        )
        task_order = TaskOrderFactory.create(create_clins=[{"number": "0002"}])
        send_task_order_files.run()

        # Check that pdf_last_sent_at has not been updated
        assert not task_order.pdf_last_sent_at


class TestCreateBillingInstructions:
    @pytest.fixture
    def unsent_clin(self):
        start_date = pendulum.now().subtract(days=1)
        portfolio = PortfolioFactory.create(
            csp_data={
                "tenant_id": str(uuid4()),
                "billing_account_name": "fake",
                "billing_profile_name": "fake",
            },
            task_orders=[{"create_clins": [{"start_date": start_date}]}],
        )
        return portfolio.task_orders[0].clins[0]

    def test_update_clin_last_sent_at(self, session, unsent_clin):
        assert not unsent_clin.last_sent_at

        # The session needs to be nested to prevent detached SQLAlchemy instance
        session.begin_nested()
        create_billing_instruction()

        # check that last_sent_at has been updated
        assert unsent_clin.last_sent_at
        session.rollback()

    def test_failure(self, monkeypatch, session, unsent_clin):
        def _create_billing_instruction(MockCloudProvider, object_name):
            raise AzureError("something went wrong")

        monkeypatch.setattr(
            "atat.domain.csp.cloud.MockCloudProvider.create_billing_instruction",
            _create_billing_instruction,
        )

        # The session needs to be nested to prevent detached SQLAlchemy instance
        session.begin_nested()
        create_billing_instruction()

        # check that last_sent_at has not been updated
        assert not unsent_clin.last_sent_at
        session.rollback()

    def test_task_order_with_multiple_clins(self, session):
        start_date = pendulum.now(tz="UTC").subtract(days=1)
        portfolio = PortfolioFactory.create(
            csp_data={
                "tenant_id": str(uuid4()),
                "billing_account_name": "fake",
                "billing_profile_name": "fake",
            },
            task_orders=[
                {
                    "create_clins": [
                        {"start_date": start_date, "last_sent_at": start_date}
                    ]
                }
            ],
        )
        task_order = portfolio.task_orders[0]
        sent_clin = task_order.clins[0]

        # Add new CLIN to the Task Order
        new_clin = CLINFactory.create(task_order=task_order)
        assert not new_clin.last_sent_at

        session.begin_nested()
        create_billing_instruction()
        session.add(sent_clin)

        # check that last_sent_at has been update for the new clin only
        assert new_clin.last_sent_at
        assert sent_clin.last_sent_at != new_clin.last_sent_at
        session.rollback()
