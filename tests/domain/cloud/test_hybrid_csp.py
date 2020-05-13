import pendulum
import pytest
from unittest.mock import Mock
from uuid import uuid4

from atat.domain.csp import HybridCSP
from atat.domain.csp.cloud.exceptions import UserProvisioningException
from atat.domain.csp.cloud.models import (
    EnvironmentCSPPayload,
    KeyVaultCredentials,
    UserCSPPayload,
    UserRoleCSPPayload,
    CostManagementQueryCSPPayload,
    InitialMgmtGroupVerificationCSPPayload,
)
from atat.jobs import do_create_application, do_create_environment_role, do_create_user
from atat.models import PortfolioStates, PortfolioStateMachine
from tests.factories import (
    ApplicationFactory,
    ApplicationRoleFactory,
    ApplicationRoleStatus,
    CLINFactory,
    EnvironmentFactory,
    EnvironmentRoleFactory,
    PortfolioFactory,
    PortfolioStateMachineFactory,
    TaskOrderFactory,
    UserFactory,
)


@pytest.fixture(scope="function")
def portfolio():
    today = pendulum.today()
    yesterday = today.subtract(days=1)
    future = today.add(days=100)

    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=owner)
    ApplicationFactory.create(portfolio=portfolio, environments=[{"name": "dev"}])

    TaskOrderFactory.create(
        portfolio=portfolio,
        signed_at=yesterday,
        clins=[CLINFactory.create(start_date=yesterday, end_date=future)],
    )

    return portfolio


@pytest.fixture(scope="function")
def csp(app):
    return HybridCSP(app, simulate_failures=True).cloud


@pytest.fixture(scope="function")
def state_machine(app, csp, portfolio):
    return PortfolioStateMachineFactory.create(portfolio=portfolio, cloud=csp)


@pytest.mark.hybrid
def test_hybrid_provision_portfolio(pytestconfig, state_machine: PortfolioStateMachine):
    csp_data = {}
    config = {"billing_account_name": "billing_account_name"}

    while state_machine.state != PortfolioStates.COMPLETED:
        collected_data = dict(
            list(csp_data.items())
            + list(state_machine.portfolio.to_dictionary().items())
            + list(config.items())
        )

        state_machine.trigger_next_transition(csp_data=collected_data)
        assert (
            "created" in state_machine.state.value
            or state_machine.state == PortfolioStates.COMPLETED
        )

        csp_data = state_machine.portfolio.csp_data


@pytest.mark.hybrid
def test_hybrid_create_application_job(session, csp):
    csp.azure.create_tenant_creds(
        csp.azure.root_tenant_id,
        KeyVaultCredentials(
            root_tenant_id=csp.azure.root_tenant_id,
            root_sp_client_id=csp.azure.client_id,
            root_sp_key=csp.azure.secret_key,
            tenant_id=csp.azure.root_tenant_id,
            tenant_sp_key=csp.azure.secret_key,
            tenant_sp_client_id=csp.azure.client_id,
        ),
    )

    portfolio = PortfolioFactory.create(
        csp_data={
            "tenant_id": csp.azure.root_tenant_id,
            "root_management_group_id": csp.azure.config["AZURE_ROOT_MGMT_GROUP_ID"],
        }
    )

    application = ApplicationFactory.create(portfolio=portfolio, cloud_id=None)
    do_create_application(csp, application.id)
    session.refresh(application)

    assert application.cloud_id


@pytest.mark.hybrid
def test_hybrid_create_environment_job(csp):
    environment = EnvironmentFactory.create()

    csp.azure.create_tenant_creds(
        csp.azure.root_tenant_id,
        KeyVaultCredentials(
            root_tenant_id=csp.azure.root_tenant_id,
            root_sp_client_id=csp.azure.client_id,
            root_sp_key=csp.azure.secret_key,
            tenant_id=csp.azure.root_tenant_id,
            tenant_sp_key=csp.azure.secret_key,
            tenant_sp_client_id=csp.azure.client_id,
        ),
    )

    payload = EnvironmentCSPPayload(
        tenant_id=csp.azure.root_tenant_id,
        display_name=environment.name,
        parent_id=csp.azure.config["AZURE_ROOT_MGMT_GROUP_ID"],
    )

    result = csp.create_environment(payload)

    assert result.id


@pytest.mark.hybrid
def test_get_reporting_data(csp):
    from_date = pendulum.now().subtract(years=1).add(days=1).format("YYYY-MM-DD")
    to_date = pendulum.now().format("YYYY-MM-DD")

    csp.azure.create_tenant_creds(
        csp.azure.root_tenant_id,
        KeyVaultCredentials(
            root_tenant_id=csp.azure.root_tenant_id,
            root_sp_client_id=csp.azure.client_id,
            root_sp_key=csp.azure.secret_key,
            tenant_id=csp.azure.root_tenant_id,
            tenant_sp_key=csp.azure.secret_key,
            tenant_sp_client_id=csp.azure.client_id,
        ),
    )

    payload = CostManagementQueryCSPPayload(
        tenant_id=csp.azure.root_tenant_id,
        from_date=from_date,
        to_date=to_date,
        billing_profile_properties={"invoice_sections": [{"invoice_section_id": "",}],},
    )

    result = csp.get_reporting_data(payload)
    assert result.name


@pytest.mark.hybrid
class TestHybridUserManagement:
    @pytest.fixture
    def portfolio(self, app, csp):
        return PortfolioFactory.create(
            csp_data={
                "tenant_id": csp.azure.root_tenant_id,
                "domain_name": f"dancorriganpromptworks",
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
            first_name=f"test-user-{uuid4()}", last_name="Solo", email="han@example.com"
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

    @pytest.fixture
    def csp(self, app):
        return HybridCSP(app).cloud

    def test_hybrid_create_user_job(self, session, csp, app_role_1, portfolio):
        csp.azure.create_tenant_creds(
            csp.azure.root_tenant_id,
            KeyVaultCredentials(
                root_tenant_id=csp.azure.root_tenant_id,
                root_sp_client_id=csp.azure.client_id,
                root_sp_key=csp.azure.secret_key,
                tenant_id=csp.azure.root_tenant_id,
                tenant_sp_key=csp.azure.secret_key,
                tenant_sp_client_id=csp.azure.client_id,
            ),
        )

        assert not app_role_1.cloud_id

        session.begin_nested()
        do_create_user(csp, [app_role_1.id])
        session.rollback()

        assert app_role_1.cloud_id

    def test_hybrid_create_user_sends_email(
        self, monkeypatch, csp, app_role_1, app_role_2
    ):
        mock = Mock()
        monkeypatch.setattr("atat.jobs.send_mail", mock)

        do_create_user(csp, [app_role_1.id, app_role_2.id])
        assert mock.call_count == 1

    def test_hybrid_user_has_tenant(self, session, csp, app_role_1, app_1, user):
        cloud_id = "123456"
        ApplicationRoleFactory.create(
            user=user,
            status=ApplicationRoleStatus.ACTIVE,
            cloud_id=cloud_id,
            application=ApplicationFactory.create(portfolio=app_1.portfolio),
        )

        session.begin_nested()
        do_create_user(csp, [app_role_1.id])
        session.rollback()

        assert app_role_1.cloud_id == cloud_id

    def test_hybrid_disable_user(self, session, csp, portfolio, app, app_role_1):
        csp.azure.create_tenant_creds(
            csp.azure.root_tenant_id,
            KeyVaultCredentials(
                root_tenant_id=csp.azure.root_tenant_id,
                root_sp_client_id=csp.azure.client_id,
                root_sp_key=csp.azure.secret_key,
                tenant_id=csp.azure.root_tenant_id,
                tenant_sp_key=csp.azure.secret_key,
                tenant_sp_client_id=csp.azure.client_id,
            ),
        )

        session.begin_nested()
        do_create_user(csp, [app_role_1.id])
        session.rollback()

        payload = UserRoleCSPPayload(
            tenant_id=csp.azure.root_tenant_id,
            role="owner",
            management_group_id=app.config["AZURE_ROOT_MGMT_GROUP_ID"],
            user_object_id=app_role_1.cloud_id,
        )

        create_user_role_result = csp.azure.create_user_role(payload)
        disable_user_result = csp.azure.disable_user(
            csp.azure.root_tenant_id, create_user_role_result.id
        )
        assert disable_user_result["id"] == create_user_role_result.id

    def test_hybrid_do_create_environment_role_job(self, session, csp, portfolio, app):
        environment_role = EnvironmentRoleFactory.create()
        environment_role.environment.cloud_id = app.config["AZURE_ROOT_MGMT_GROUP_ID"]
        environment_role.application_role.cloud_id = app.config["AZURE_USER_OBJECT_ID"]
        environment_role.environment.portfolio.csp_data = {
            "tenant_id": csp.azure.root_tenant_id,
            "domain_name": "dancorriganpromptworks",
        }

        session.commit()

        csp.azure.create_tenant_creds(
            csp.azure.root_tenant_id,
            KeyVaultCredentials(
                root_tenant_id=csp.azure.root_tenant_id,
                root_sp_client_id=csp.azure.client_id,
                root_sp_key=csp.azure.secret_key,
                tenant_id=csp.azure.root_tenant_id,
                tenant_sp_key=csp.azure.secret_key,
                tenant_sp_client_id=csp.azure.client_id,
            ),
        )

        try:
            do_create_environment_role(csp, environment_role.id)
        except UserProvisioningException as e:
            if "RoleAssignmentExists" not in str(e):
                raise e


@pytest.mark.hybrid
def test_create_user(csp):
    payload = UserCSPPayload(
        tenant_id=csp.azure.root_tenant_id,
        display_name="Test Testerson",
        tenant_host_name="testtenant",
        email="test@testerson.test",
        password="asdfghjkl",  # pragma: allowlist secret
    )

    result = csp.azure.create_user(payload)
    assert result.id
