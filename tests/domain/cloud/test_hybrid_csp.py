import collections.abc
import json
import pendulum
import pytest
import re
from copy import deepcopy
from typing import Dict, List
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
    SubscriptionCreationCSPPayload,
    SubscriptionVerificationCSPPayload,
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
from vcr import VCR


REDACTION_STRING = "*****"
UUID_RE = (
    r"[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"
)
HASH_RE = r"[0-9a-fA-F]{32}"
ROLE_ASSIGNMENT_RE = r"\/providers\/Microsoft\.Management\/managementGroups\/.*\/providers\/Microsoft\.Authorization\/roleAssignments/"


def path_with_exceptions(r1, r2):
    """VCR request matcher that makes a special exceptions for the api calls
    that use random UUIDs in their paths. In this case, we give these paths
    a "pass" by saying they *do* match even if the UUID portions do not.

    ## Params

    r1 - incoming request
    r2 - existing (cached) request
    """

    login_url = "login.microsoftonline.com"
    if r1.host == login_url and r2.host == login_url:
        return True

    matcher = ROLE_ASSIGNMENT_RE
    if re.match(matcher, r1.path) and re.match(matcher, r2.path):
        return True

    matcher = r"\/providers\/Microsoft\.Management\/managementGroups\/.*"
    if re.match(matcher, r1.path) and re.match(matcher, r2.path):
        return True

    matcher = r"\/secrets\/.*"
    if re.match(matcher, r1.path) and re.match(matcher, r2.path):
        return True

    # If the request pair doesn't fall under any of the above mentioned
    # exceptions, then revert to the default path behaviour specified here:
    #
    # https://github.com/kevin1024/vcrpy/blob/master/vcr/matchers.py#L31`
    assert r1.path == r2.path, "{} != {}".format(r1.path, r2.path)


default_matchers = ["method", "scheme", "host", "port", "query"]


def redact(target: Dict, replace: List, redaction: str = REDACTION_STRING) -> Dict:
    """Recursivly traverse a dictionary, replacing any `replace` keys found in 
    `target` with values specified by `replace`.
    
    ## Example

    ```python
    target = {"A": {"B": "secret", "C": "secret"}}
    replace = ["B", "C"]
    redact(target, replace)  # {"A": {"B": `redaction`, "C": `redaction`}}
    ```
    """

    t = deepcopy(target)
    for k, v in target.items():
        if k in replace:
            t[k] = redaction
        elif isinstance(v, collections.abc.Mapping):
            t[k] = redact(v, replace)
    return t


def before_record_request(request):
    if "vault.azure.net" in request.host:
        if re.match(r"/secrets/.*", request.path):
            request.uri = re.sub(
                r".*\.vault.azure.net", "https://my-vault.vault.azure.net", request.uri,
            )
            request.uri = re.sub(
                r"\/secret.*$", f"/secret/{REDACTION_STRING}", request.uri
            )
            request.body = REDACTION_STRING
    if "https://login.microsoftonline.com" in request.uri:
        request.body = REDACTION_STRING
    if "https://graph.microsoft.com/v1.0/users" in request.uri:
        request.body = REDACTION_STRING
    request.uri = re.sub(UUID_RE, REDACTION_STRING, request.uri)
    request.uri = re.sub(HASH_RE, REDACTION_STRING, request.uri)

    if isinstance(request.body, bytes):
        body = request.body.decode()
        body = re.sub(UUID_RE, REDACTION_STRING, body)
        body = re.sub(HASH_RE, REDACTION_STRING, body)
        request.body = body.encode()
    return request


def before_record_response(response):
    try:
        if response["headers"].get("WWW-Authenticate"):
            response["headers"]["WWW-Authenticate"] = "*****"
        if response["headers"].get("Location"):
            response["headers"]["Location"] = "*****"
        string = response["body"]["string"]
        if isinstance(string, bytes):
            string = string.decode()
        string = re.sub(HASH_RE, REDACTION_STRING, string)
        string = re.sub(UUID_RE, REDACTION_STRING, string)
        string = redact(json.loads(string), ["access_token"])

        if string.get("id"):
            if re.match(r".*/secrets/.*", string["id"]):
                string["id"] = re.sub(
                    r".*\.vault.azure.net",
                    "https://my-vault.vault.azure.net",
                    string["id"],
                )
                string["id"] = re.sub(
                    r"\/secret.*$", f"/secret/{REDACTION_STRING}", string["id"]
                )

        if isinstance(string.get("value"), str):
            value = redact(
                json.loads(string["value"]),
                [
                    "root_sp_client_id",
                    "root_sp_key",
                    "root_tenant_id",
                    "tenant_id",
                    "tenant_admin_username",
                    "tenant_admin_password",
                    "tenant_sp_client_id",
                    "tenant_sp_key",
                ],
            )

            string["value"] = json.dumps(value)

        response["body"]["string"] = json.dumps(string).encode()
    except UnicodeDecodeError:
        pass
    except json.JSONDecodeError:
        pass
    return response


hybrid_vcr = VCR(
    path_transformer=VCR.ensure_suffix(".yaml"),
    filter_headers=["Authorization"],
    filter_query_parameters=["client_id", "client_secret", ""],
    before_record_request=before_record_request,
    before_record_response=before_record_response,
)

hybrid_vcr.register_matcher("path_with_exceptions", path_with_exceptions)
hybrid_vcr.match_on = default_matchers + ["path_with_exceptions"]
hybrid_vcr.cassette_library_dir = "tests/fixtures/cassettes"


@pytest.fixture(scope="function")
def portfolio(csp, app):
    today = pendulum.today()
    yesterday = today.subtract(days=1)
    future = today.add(days=100)

    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(
        owner=owner,
        csp_data={
            "tenant_id": csp.mock_tenant_id,
            "domain_name": app.config["AZURE_HYBRID_TENANT_DOMAIN"],
            "root_management_group_id": csp.hybrid_tenant_id,
        },
    )

    TaskOrderFactory.create(
        portfolio=portfolio,
        signed_at=yesterday,
        clins=[CLINFactory.create(start_date=yesterday, end_date=future)],
    )

    return portfolio


@pytest.fixture(scope="function")
def csp(app):
    app.config["AZURE_CLIENT_ID"] = app.config["AZURE_CLIENT_ID"] or str(uuid4())
    app.config["AZURE_SECRET_KEY"] = app.config["AZURE_SECRET_KEY"] or str(uuid4())
    app.config["AZURE_TENANT_ID"] = app.config["AZURE_TENANT_ID"] or str(uuid4())
    app.config["AZURE_VAULT_URL"] = (
        app.config["AZURE_VAULT_URL"] or "https://my-vault.vault.azure.net/"
    )
    app.config["AZURE_ROOT_MGMT_GROUP_ID"] = app.config[
        "AZURE_ROOT_MGMT_GROUP_ID"
    ] or str(uuid4())
    app.config["AZURE_USER_OBJECT_ID"] = app.config["AZURE_USER_OBJECT_ID"] or str(
        uuid4()
    )

    return HybridCSP(app, simulate_failures=False).cloud


@pytest.fixture(scope="function")
def state_machine(app, csp, portfolio):
    return PortfolioStateMachineFactory.create(portfolio=portfolio, cloud=csp)


@hybrid_vcr.use_cassette()
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


@hybrid_vcr.use_cassette()
def test_hybrid_create_application_job(session, csp):
    csp.azure.create_tenant_creds(
        csp.azure.tenant_id,
        KeyVaultCredentials(
            root_tenant_id=csp.azure.tenant_id,
            root_sp_client_id=csp.azure.client_id,
            root_sp_key=csp.azure.secret_key,
            tenant_id=csp.azure.tenant_id,
            tenant_sp_key=csp.azure.secret_key,
            tenant_sp_client_id=csp.azure.client_id,
        ),
    )

    portfolio = PortfolioFactory.create(
        csp_data={
            "tenant_id": csp.azure.tenant_id,
            "root_management_group_id": csp.azure.config["AZURE_ROOT_MGMT_GROUP_ID"],
        }
    )

    application = ApplicationFactory.create(portfolio=portfolio, cloud_id=None)

    do_create_application(csp, application.id)
    session.refresh(application)

    assert application.cloud_id


@hybrid_vcr.use_cassette()
def test_hybrid_create_environment_job(session, csp):
    environment = EnvironmentFactory.create()

    payload = EnvironmentCSPPayload(
        tenant_id=csp.hybrid_tenant_id,
        display_name=environment.name,
        parent_id=csp.hybrid_tenant_id,
    )

    result = csp.create_environment(payload)

    assert result.id


@hybrid_vcr.use_cassette()
def test_get_reporting_data(csp):
    from_date = pendulum.now().subtract(years=1).add(days=1).format("YYYY-MM-DD")
    to_date = pendulum.now().format("YYYY-MM-DD")

    payload = CostManagementQueryCSPPayload(
        tenant_id=csp.azure.root_tenant_id,
        from_date=from_date,
        to_date=to_date,
        billing_profile_properties={"invoice_sections": [{"invoice_section_id": "",}],},
    )

    result = csp.get_reporting_data(payload)
    assert result.name


@pytest.mark.hybrid
@pytest.mark.xfail(reason="This test cannot complete due to permission issues.")
def test_create_subscription(csp):
    environment = EnvironmentFactory.create()


class TestHybridUserManagement:
    @pytest.fixture
    def portfolio(self, app, csp):
        return PortfolioFactory.create(
            csp_data={
                "tenant_id": csp.azure.tenant_id,
                "domain_name": f"dancorriganpromptworks",
            }
        )

    payload = SubscriptionCreationCSPPayload(
        display_name=environment.name,
        tenant_id=csp.mock_tenant_id,
        parent_group_id=csp.hybrid_tenant_id,
        billing_account_name=csp.azure.config["AZURE_BILLING_ACCOUNT_NAME"],
        billing_profile_name=csp.azure.config["AZURE_BILLING_PROFILE_ID"],
        invoice_section_name=csp.azure.config["AZURE_INVOICE_SECTION_ID"],
    )

    csp.create_subscription_creation(payload)


@pytest.mark.hybrid
def test_create_subscription_mocked(csp):
    # TODO: When we finally move over to azure, this mocked test should
    # probably be removed in favor of the above "test_create_subscription"
    # test.
    payload = SubscriptionCreationCSPPayload(
        tenant_id="tenant id",
        displayName="display name",
        parentGroupId="parent group id",
        billingAccountName="billing account name",
        billingProfileName="billing profile name",
        invoiceSectionName="invoice section name",
    )

    sub = csp.create_subscription(payload)
    sub_creation = csp.create_subscription_creation(payload)

    assert (
        sub.subscription_verify_url
        == sub_creation.subscription_verify_url
        == "https://zombo.com"
    )
    assert sub.subscription_retry_after == sub_creation.subscription_retry_after == 10


@pytest.mark.hybrid
def test_create_subscription_verification(csp):
    payload = SubscriptionVerificationCSPPayload(
        tenantId="tenant id", subscriptionVerifyUrl="subscription verify url"
    )
    assert csp.create_subscription_verification(payload).subscription_id


@pytest.mark.hybrid
class TestHybridUserManagement:
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

    @hybrid_vcr.use_cassette()
    def test_hybrid_create_user_job(self, session, csp, app_role_1, portfolio):
        assert not app_role_1.cloud_id

        session.begin_nested()
        do_create_user(csp, [app_role_1.id])
        session.rollback()

        assert app_role_1.cloud_id

    @hybrid_vcr.use_cassette()
    def test_hybrid_create_user_sends_email(
        self, monkeypatch, csp, app_role_1, app_role_2
    ):
        mock = Mock()
        monkeypatch.setattr("atat.jobs.send_mail", mock)

        do_create_user(csp, [app_role_1.id, app_role_2.id])
        assert mock.call_count == 1

    @hybrid_vcr.use_cassette()
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

    @hybrid_vcr.use_cassette()
    def test_hybrid_disable_user(self, session, csp, portfolio, app, app_role_1):
        session.begin_nested()
        do_create_user(csp, [app_role_1.id])
        session.rollback()

        payload = UserRoleCSPPayload(
            tenant_id=csp.mock_tenant_id,
            role="owner",
            management_group_id=csp.hybrid_tenant_id,
            user_object_id=app_role_1.cloud_id,
        )

        create_user_role_result = csp.azure.create_user_role(payload)
        disable_user_result = csp.azure.disable_user(
            csp.mock_tenant_id, create_user_role_result.id
        )

        assert re.match(ROLE_ASSIGNMENT_RE, disable_user_result["id"])
        assert re.match(ROLE_ASSIGNMENT_RE, create_user_role_result.id)

    @hybrid_vcr.use_cassette()
    def test_hybrid_do_create_environment_role_job(self, session, csp, portfolio, app):
        environment_role = EnvironmentRoleFactory.create()
        environment_role.environment.cloud_id = csp.hybrid_tenant_id
        environment_role.application_role.cloud_id = app.config["AZURE_USER_OBJECT_ID"]
        environment_role.environment.portfolio.csp_data = {
            "tenant_id": csp.mock_tenant_id,
            "domain_name": app.config["AZURE_HYBRID_TENANT_DOMAIN"],
        }

        session.commit()

        try:
            do_create_environment_role(csp, environment_role.id)
        except UserProvisioningException as e:
            if "RoleAssignmentExists" not in str(e):
                raise e


@pytest.mark.hybrid
def test_create_user(csp):
    payload = UserCSPPayload(
        tenant_id=csp.mock_tenant_id,
        display_name="Test Testerson",
        tenant_host_name="testtenant",
        email="test@testerson.test",
        password="asdfghjkl",  # pragma: allowlist secret
    )

    result = csp.azure.create_user(payload)
    assert result.id
