import json
from unittest.mock import Mock, patch
from uuid import uuid4

import pendulum
import pydantic
import pytest
from adal.adal_error import AdalError
from tests.factories import ApplicationFactory, EnvironmentFactory
from tests.mock_azure import mock_azure, MOCK_ACCESS_TOKEN  # pylint: disable=W0611
from tests.mock_azure import AZURE_CONFIG, MockAzureSDK

from atat.domain.csp.cloud import AzureCloudProvider
from atat.domain.csp.cloud.exceptions import (
    AuthenticationException,
    ConnectionException,
    DomainNameException,
    UnknownServerException,
    UserProvisioningException,
)
from atat.domain.csp.cloud.models import (
    AdminRoleDefinitionCSPPayload,
    AdminRoleDefinitionCSPResult,
    ApplicationCSPPayload,
    ApplicationCSPResult,
    BillingInstructionCSPPayload,
    BillingInstructionCSPResult,
    BillingOwnerCSPPayload,
    BillingProfileCreationCSPPayload,
    BillingProfileCreationCSPResult,
    BillingProfileTenantAccessCSPPayload,
    BillingProfileTenantAccessCSPResult,
    BillingProfileVerificationCSPPayload,
    BillingProfileVerificationCSPResult,
    CostManagementQueryCSPPayload,
    CostManagementQueryCSPResult,
    EnvironmentCSPPayload,
    InitialMgmtGroupCSPPayload,
    InitialMgmtGroupCSPResult,
    InitialMgmtGroupVerificationCSPPayload,
    InitialMgmtGroupVerificationCSPResult,
    KeyVaultCredentials,
    PoliciesCSPPayload,
    PoliciesCSPResult,
    PrincipalAdminRoleCSPPayload,
    PrincipalAdminRoleCSPResult,
    ProductPurchaseCSPPayload,
    ProductPurchaseCSPResult,
    ProductPurchaseVerificationCSPPayload,
    ProductPurchaseVerificationCSPResult,
    SubscriptionCreationCSPPayload,
    SubscriptionCreationCSPResult,
    SubscriptionVerificationCSPPayload,
    SuscriptionVerificationCSPResult,
    TaskOrderBillingCreationCSPPayload,
    TaskOrderBillingCreationCSPResult,
    TaskOrderBillingVerificationCSPPayload,
    TaskOrderBillingVerificationCSPResult,
    TenantAdminCredentialResetCSPPayload,
    TenantAdminOwnershipCSPPayload,
    TenantAdminOwnershipCSPResult,
    TenantCSPPayload,
    TenantCSPResult,
    TenantPrincipalAppCSPPayload,
    TenantPrincipalAppCSPResult,
    TenantPrincipalCredentialCSPPayload,
    TenantPrincipalCredentialCSPResult,
    TenantPrincipalCSPPayload,
    TenantPrincipalCSPResult,
    TenantPrincipalOwnershipCSPPayload,
    TenantPrincipalOwnershipCSPResult,
    UserCSPPayload,
    UserRoleCSPPayload,
)

BILLING_ACCOUNT_NAME = "52865e4c-52e8-5a6c-da6b-c58f0814f06f:7ea5de9d-b8ce-4901-b1c5-d864320c7b03_2019-05-31"


def mock_requests_response(
    status=200,
    content="CONTENT",
    json_data=None,
    raise_for_status=None,
    headers=None,
    ok=True,
):
    mock_resp = Mock()
    # mock raise_for_status call w/optional error
    mock_resp.raise_for_status = Mock()
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status
    # set status code and content
    mock_resp.status_code = status
    mock_resp.ok = ok
    mock_resp.headers = headers if headers is not None else {}
    mock_resp.content = content
    # add json data if provided
    mock_resp.json.return_value = json_data if json_data is not None else {}
    return mock_resp


@pytest.fixture(scope="function", autouse=True)
def mock_http_error_response(mock_azure):
    response = mock_requests_response(
        status=500,
        raise_for_status=mock_azure.sdk.requests.exceptions.HTTPError(
            "500 Server Error"
        ),
    )
    return response


@pytest.fixture(scope="function")
def unmocked_cloud_provider():
    azure_cloud_provider = AzureCloudProvider(AZURE_CONFIG)
    return azure_cloud_provider


def mock_management_group_create(mock_azure, spec_dict):
    mock_azure.sdk.managementgroups.ManagementGroupsAPI.return_value.management_groups.create_or_update.return_value.result.return_value = (
        spec_dict
    )


def test_create_environment_succeeds(mock_azure: AzureCloudProvider):
    environment = EnvironmentFactory.create()
    mock_management_group_create(mock_azure, {"id": "Test Id"})

    payload = EnvironmentCSPPayload(
        tenant_id="1234", display_name=environment.name, parent_id=str(uuid4())
    )
    result = mock_azure.create_environment(payload)

    assert result.id == "Test Id"


def test_create_application_succeeds(mock_azure: AzureCloudProvider):
    application = ApplicationFactory.create()
    mock_management_group_create(mock_azure, {"id": "Test Id"})

    payload = ApplicationCSPPayload(
        tenant_id="1234", display_name=application.name, parent_id=str(uuid4())
    )

    result: ApplicationCSPResult = mock_azure.create_application(payload)

    assert result.id == "Test Id"


def test_create_initial_mgmt_group_succeeds(mock_azure: AzureCloudProvider):
    application = ApplicationFactory.create()
    mock_management_group_create(mock_azure, {"id": "Test Id", "name": "Test Name"})

    payload = InitialMgmtGroupCSPPayload(
        tenant_id="1234",
        display_name=application.name,
        management_group_name=str(uuid4()),
    )
    result: InitialMgmtGroupCSPResult = mock_azure.create_initial_mgmt_group(payload)

    assert result.root_management_group_id == "Test Id"
    assert result.root_management_group_name == "Test Name"


def test_create_initial_mgmt_group_verification(
    mock_azure: AzureCloudProvider, mock_http_error_response
):
    mock_id = "management/group/path/TestName"

    mock_azure.sdk.requests.get.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_requests_response(json_data={"id": mock_id}),
    ]

    payload = InitialMgmtGroupVerificationCSPPayload(
        tenant_id="1234", management_group_name="TestName"
    )

    with pytest.raises(ConnectionException):
        mock_azure.create_initial_mgmt_group_verification(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_initial_mgmt_group_verification(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_initial_mgmt_group_verification(payload)

    result: InitialMgmtGroupVerificationCSPResult = mock_azure.create_initial_mgmt_group_verification(
        payload
    )

    assert result.id == mock_id


def test_disable_user(mock_azure: AzureCloudProvider, mock_http_error_response):

    assignment_guid = str(uuid4())
    management_group_id = str(uuid4())
    assignment_id = f"/providers/Microsoft.Management/managementGroups/{management_group_id}/providers/Microsoft.Authorization/roleAssignments/{assignment_guid}"
    mock_result = mock_requests_response(
        json_data={
            "properties": {
                "roleDefinitionId": "/subscriptions/subId/providers/Microsoft.Authorization/roleDefinitions/roledefinitionId",
                "principalId": "Pid",
                "scope": "/subscriptions/subId/resourcegroups/rgname",
            },
            "id": assignment_id,
            "type": "Microsoft.Authorization/roleAssignments",
            "name": assignment_guid,
        }
    )

    mock_azure.sdk.requests.delete.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    tenant_id = "60ff9d34-82bf-4f21-b565-308ef0533435"
    with pytest.raises(ConnectionException):
        mock_azure.disable_user(tenant_id, assignment_guid)
    with pytest.raises(ConnectionException):
        mock_azure.disable_user(tenant_id, assignment_guid)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.disable_user(tenant_id, assignment_guid)

    result = mock_azure.disable_user(tenant_id, assignment_guid)
    assert result.get("name") == assignment_guid


def test_create_tenant(mock_azure: AzureCloudProvider, mock_http_error_response):
    mock_result = mock_requests_response(
        json_data={
            "objectId": "0a5f4926-e3ee-4f47-a6e3-8b0a30a40e3d",
            "tenantId": "60ff9d34-82bf-4f21-b565-308ef0533435",
            "userId": "1153801116406515559",
        }
    )

    mock_azure.sdk.requests.post.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]
    payload = TenantCSPPayload(
        **dict(
            user_id="admin",
            password="JediJan13$coot",  # pragma: allowlist secret
            domain_name="jediccpospawnedtenant2",
            first_name="Tedry",
            last_name="Tenet",
            country_code="US",
            password_recovery_email_address="thomas@promptworks.com",
        )
    )

    with pytest.raises(ConnectionException):
        mock_azure.create_tenant(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_tenant(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_tenant(payload)

    result: TenantCSPResult = mock_azure.create_tenant(payload)
    assert result.tenant_id == "60ff9d34-82bf-4f21-b565-308ef0533435"


def test_create_billing_profile_creation(
    mock_azure: AzureCloudProvider, mock_http_error_response
):
    mock_result = mock_requests_response(
        headers={"Location": "http://retry-url", "Retry-After": "10",}, status=202
    )

    mock_azure.sdk.requests.post.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = BillingProfileCreationCSPPayload(
        **dict(
            address=dict(
                address_line_1="123 S Broad Street, Suite 2400",
                company_name="Promptworks",
                city="Philadelphia",
                region="PA",
                country="US",
                postal_code="19109",
            ),
            tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
            billing_profile_display_name="Test Billing Profile",
            billing_account_name=BILLING_ACCOUNT_NAME,
        )
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_billing_profile_creation(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_billing_profile_creation(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_billing_profile_creation(payload)

    body: BillingProfileCreationCSPResult = mock_azure.create_billing_profile_creation(
        payload
    )
    assert body.billing_profile_retry_after == 10


def test_validate_billing_profile_creation(
    mock_azure: AzureCloudProvider, mock_http_error_response
):

    mock_result = mock_requests_response(
        json_data={
            "id": "/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/billingProfiles/KQWI-W2SU-BG7-TGB",
            "name": "KQWI-W2SU-BG7-TGB",
            "properties": {
                "address": {
                    "addressLine1": "123 S Broad Street, Suite 2400",
                    "city": "Philadelphia",
                    "companyName": "Promptworks",
                    "country": "US",
                    "postalCode": "19109",
                    "region": "PA",
                },
                "currency": "USD",
                "displayName": "First Portfolio Billing Profile",
                "enabledAzurePlans": [],
                "hasReadAccess": True,
                "invoiceDay": 5,
                "invoiceEmailOptIn": False,
                "invoiceSections": [
                    {
                        "id": "/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/billingProfiles/KQWI-W2SU-BG7-TGB/invoiceSections/6HMZ-2HLO-PJA-TGB",
                        "name": "6HMZ-2HLO-PJA-TGB",
                        "properties": {
                            "displayName": "First Portfolio Billing Profile"
                        },
                        "type": "Microsoft.Billing/billingAccounts/billingProfiles/invoiceSections",
                    }
                ],
            },
            "type": "Microsoft.Billing/billingAccounts/billingProfiles",
        }
    )

    mock_azure.sdk.requests.get.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = BillingProfileVerificationCSPPayload(
        **dict(
            tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
            billing_profile_verify_url="https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/createBillingProfile_478d5706-71f9-4a8b-8d4e-2cbaca27a668?api-version=2019-10-01-preview",
        )
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_billing_profile_verification(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_billing_profile_verification(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_billing_profile_verification(payload)

    body: BillingProfileVerificationCSPResult = mock_azure.create_billing_profile_verification(
        payload
    )
    assert body.billing_profile_name == "KQWI-W2SU-BG7-TGB"
    assert (
        body.billing_profile_properties.billing_profile_display_name
        == "First Portfolio Billing Profile"
    )


def test_create_billing_profile_tenant_access(
    mock_azure: AzureCloudProvider, mock_http_error_response
):

    mock_result = mock_requests_response(
        status=201,
        json_data={
            "id": "/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/billingProfiles/KQWI-W2SU-BG7-TGB/billingRoleAssignments/40000000-aaaa-bbbb-cccc-100000000000_0a5f4926-e3ee-4f47-a6e3-8b0a30a40e3d",
            "name": "40000000-aaaa-bbbb-cccc-100000000000_0a5f4926-e3ee-4f47-a6e3-8b0a30a40e3d",
            "properties": {
                "createdOn": "2020-01-14T14:39:26.3342192+00:00",
                "createdByPrincipalId": "82e2b376-3297-4096-8743-ed65b3be0b03",
                "principalId": "0a5f4926-e3ee-4f47-a6e3-8b0a30a40e3d",
                "principalTenantId": "60ff9d34-82bf-4f21-b565-308ef0533435",
                "roleDefinitionId": "/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/billingProfiles/KQWI-W2SU-BG7-TGB/billingRoleDefinitions/40000000-aaaa-bbbb-cccc-100000000000",
                "scope": "/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/billingProfiles/KQWI-W2SU-BG7-TGB",
            },
            "type": "Microsoft.Billing/billingRoleAssignments",
        },
    )

    mock_azure.sdk.requests.post.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = BillingProfileTenantAccessCSPPayload(
        **dict(
            tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
            user_object_id="0a5f4926-e3ee-4f47-a6e3-8b0a30a40e3d",
            billing_account_name="7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31",
            billing_profile_name="KQWI-W2SU-BG7-TGB",
        )
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_billing_profile_tenant_access(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_billing_profile_tenant_access(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_billing_profile_tenant_access(payload)

    body: BillingProfileTenantAccessCSPResult = mock_azure.create_billing_profile_tenant_access(
        payload
    )
    assert (
        body.billing_role_assignment_name
        == "40000000-aaaa-bbbb-cccc-100000000000_0a5f4926-e3ee-4f47-a6e3-8b0a30a40e3d"
    )


def test_create_task_order_billing_creation(
    mock_azure: AzureCloudProvider, mock_http_error_response
):

    mock_result = mock_requests_response(
        status=202,
        headers={
            "Location": "https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/patchBillingProfile_KQWI-W2SU-BG7-TGB:02715576-4118-466c-bca7-b1cd3169ff46?api-version=2019-10-01-preview",
            "Retry-After": "10",
        },
    )

    mock_azure.sdk.requests.patch.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = TaskOrderBillingCreationCSPPayload(
        **dict(
            tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
            billing_account_name="7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31",
            billing_profile_name="KQWI-W2SU-BG7-TGB",
        )
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_task_order_billing_creation(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_task_order_billing_creation(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_task_order_billing_creation(payload)

    body: TaskOrderBillingCreationCSPResult = mock_azure.create_task_order_billing_creation(
        payload
    )

    assert (
        body.task_order_billing_verify_url
        == "https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/patchBillingProfile_KQWI-W2SU-BG7-TGB:02715576-4118-466c-bca7-b1cd3169ff46?api-version=2019-10-01-preview"
    )


def test_create_task_order_billing_verification(mock_azure, mock_http_error_response):

    mock_result = mock_requests_response(
        json_data={
            "id": "/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/billingProfiles/KQWI-W2SU-BG7-TGB",
            "name": "KQWI-W2SU-BG7-TGB",
            "properties": {
                "address": {
                    "addressLine1": "123 S Broad Street, Suite 2400",
                    "city": "Philadelphia",
                    "companyName": "Promptworks",
                    "country": "US",
                    "postalCode": "19109",
                    "region": "PA",
                },
                "currency": "USD",
                "displayName": "Test Billing Profile",
                "enabledAzurePlans": [
                    {
                        "productId": "DZH318Z0BPS6",
                        "skuId": "0001",
                        "skuDescription": "Microsoft Azure Plan",
                    }
                ],
                "hasReadAccess": True,
                "invoiceDay": 5,
                "invoiceEmailOptIn": False,
                "invoiceSections": [
                    {
                        "id": "/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/billingProfiles/KQWI-W2SU-BG7-TGB/invoiceSections/CHCO-BAAR-PJA-TGB",
                        "name": "CHCO-BAAR-PJA-TGB",
                        "properties": {"displayName": "Test Billing Profile"},
                        "type": "Microsoft.Billing/billingAccounts/billingProfiles/invoiceSections",
                    }
                ],
            },
            "type": "Microsoft.Billing/billingAccounts/billingProfiles",
        }
    )

    mock_azure.sdk.requests.get.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = TaskOrderBillingVerificationCSPPayload(
        **dict(
            tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
            task_order_billing_verify_url="https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/createBillingProfile_478d5706-71f9-4a8b-8d4e-2cbaca27a668?api-version=2019-10-01-preview",
        )
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_task_order_billing_verification(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_task_order_billing_verification(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_task_order_billing_verification(payload)

    body: TaskOrderBillingVerificationCSPResult = mock_azure.create_task_order_billing_verification(
        payload
    )
    assert body.billing_profile_name == "KQWI-W2SU-BG7-TGB"
    assert (
        body.billing_profile_enabled_plan_details.enabled_azure_plans[0].get("skuId")
        == "0001"
    )


def test_create_billing_instruction(
    mock_azure: AzureCloudProvider, mock_http_error_response
):

    mock_result = mock_requests_response(
        json_data={
            "name": "TO1:CLIN001",
            "properties": {
                "amount": 1000.0,
                "endDate": "2020-03-01T00:00:00+00:00",
                "startDate": "2020-01-01T00:00:00+00:00",
            },
            "type": "Microsoft.Billing/billingAccounts/billingProfiles/billingInstructions",
        }
    )

    mock_azure.sdk.requests.put.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = BillingInstructionCSPPayload(
        **dict(
            tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
            initial_clin_amount=1000.00,
            initial_clin_start_date="2020/1/1",
            initial_clin_end_date="2020/3/1",
            initial_clin_type="1",
            initial_task_order_id="TO1",
            billing_account_name="7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31",
            billing_profile_name="KQWI-W2SU-BG7-TGB",
        )
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_billing_instruction(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_billing_instruction(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_billing_instruction(payload)
    body: BillingInstructionCSPResult = mock_azure.create_billing_instruction(payload)
    assert body.reported_clin_name == "TO1:CLIN001"


def test_create_product_purchase(
    mock_azure: AzureCloudProvider, mock_http_error_response
):
    mock_result = mock_requests_response(
        status=202,
        headers={
            "Location": "https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/patchBillingProfile_KQWI-W2SU-BG7-TGB:02715576-4118-466c-bca7-b1cd3169ff46?api-version=2019-10-01-preview",
            "Retry-After": "10",
        },
    )

    mock_azure.sdk.requests.post.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = ProductPurchaseCSPPayload(
        **dict(
            tenant_id="6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
            billing_account_name="7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31",
            billing_profile_name="KQWI-W2SU-BG7-TGB",
        )
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_product_purchase(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_product_purchase(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_product_purchase(payload)

    body: ProductPurchaseCSPResult = mock_azure.create_product_purchase(payload)
    assert (
        body.product_purchase_verify_url
        == "https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/patchBillingProfile_KQWI-W2SU-BG7-TGB:02715576-4118-466c-bca7-b1cd3169ff46?api-version=2019-10-01-preview"
    )


def test_create_product_purchase_verification(mock_azure, mock_http_error_response):

    mock_result = mock_requests_response(
        json_data={
            "id": "/providers/Microsoft.Billing/billingAccounts/BILLINGACCOUNTNAME/billingProfiles/BILLINGPROFILENAME/invoiceSections/INVOICESECTION/products/29386e29-a025-faae-f70b-b1cbbc266600",
            "name": "29386e29-a025-faae-f70b-b1cbbc266600",
            "properties": {
                "availabilityId": "C07TTFC7Q9XK",
                "billingProfileId": "/providers/Microsoft.Billing/billingAccounts/BILLINGACCOUNTNAME/billingProfiles/BILLINGPROFILENAME",
                "billingProfileDisplayName": "ATAT Billing Profile",
                "endDate": "01/30/2021",
                "invoiceSectionId": "/providers/Microsoft.Billing/billingAccounts/BILLINGACCOUNTNAME/billingProfiles/BILLINGPROFILENAME/invoiceSections/INVOICESECTION",
                "invoiceSectionDisplayName": "ATAT Billing Profile",
                "productType": "Azure Active Directory Premium P1",
                "productTypeId": "C07TTFC7Q9XK",
                "skuId": "0002",
                "skuDescription": "Azure Active Directory Premium P1",
                "purchaseDate": "01/31/2020",
                "quantity": 5,
                "status": "AutoRenew",
            },
            "type": "Microsoft.Billing/billingAccounts/billingProfiles/invoiceSections/products",
        }
    )

    mock_azure.sdk.requests.get.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = ProductPurchaseVerificationCSPPayload(
        **dict(
            tenant_id="6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
            product_purchase_verify_url="https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/createBillingProfile_478d5706-71f9-4a8b-8d4e-2cbaca27a668?api-version=2019-10-01-preview",
        )
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_product_purchase_verification(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_product_purchase_verification(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_product_purchase_verification(payload)

    body: ProductPurchaseVerificationCSPResult = mock_azure.create_product_purchase_verification(
        payload
    )
    assert body.premium_purchase_date == "01/31/2020"


def test_create_tenant_principal_app(
    mock_azure: AzureCloudProvider, mock_http_error_response
):
    mock_result = mock_requests_response(json_data={"appId": "appId", "id": "id"})

    mock_azure.sdk.requests.post.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = TenantPrincipalAppCSPPayload(
        **{
            "tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
            "display_name": "ATAT Remote Admin :: Test",
        }
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_tenant_principal_app(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_tenant_principal_app(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_tenant_principal_app(payload)

    result: TenantPrincipalAppCSPResult = mock_azure.create_tenant_principal_app(
        payload
    )

    assert result.principal_app_id == "appId"


def test_create_tenant_principal(
    mock_azure: AzureCloudProvider, mock_http_error_response
):
    mock_result = mock_requests_response(json_data={"id": "principal_id"})

    mock_azure.sdk.requests.post.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = TenantPrincipalCSPPayload(
        **{
            "tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
            "principal_app_id": "appId",
        }
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_tenant_principal(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_tenant_principal(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_tenant_principal(payload)

    result: TenantPrincipalCSPResult = mock_azure.create_tenant_principal(payload)

    assert result.principal_id == "principal_id"


def test_create_tenant_principal_credential(
    mock_azure: AzureCloudProvider, mock_http_error_response
):
    mock_result = mock_requests_response(json_data={"secretText": "new secret key"})

    mock_azure.sdk.requests.post.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = TenantPrincipalCredentialCSPPayload(
        **{
            "tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
            "principal_app_id": "appId",
            "principal_app_object_id": "appObjId",
        }
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_tenant_principal_credential(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_tenant_principal_credential(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_tenant_principal_credential(payload)

    result: TenantPrincipalCredentialCSPResult = mock_azure.create_tenant_principal_credential(
        payload
    )

    assert result.principal_creds_established == True


def test_create_admin_role_definition(
    mock_azure: AzureCloudProvider, mock_http_error_response
):

    mock_result = mock_requests_response(
        json_data={
            "value": [
                {"id": "wrongid", "displayName": "Wrong Role"},
                {"id": "id", "displayName": "Company Administrator"},
            ]
        }
    )

    mock_azure.sdk.requests.get.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = AdminRoleDefinitionCSPPayload(
        **{"tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4"}
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_admin_role_definition(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_admin_role_definition(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_admin_role_definition(payload)

    result: AdminRoleDefinitionCSPResult = mock_azure.create_admin_role_definition(
        payload
    )

    assert result.admin_role_def_id == "id"


def test_create_tenant_admin_ownership(
    mock_azure: AzureCloudProvider, mock_http_error_response
):
    mock_result = mock_requests_response(json_data={"id": "id"})

    mock_azure.sdk.requests.put.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = TenantAdminOwnershipCSPPayload(
        **{
            "tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
            "user_object_id": "971efe4d-1e80-4e39-b3b9-4e5c63ad446d",
        }
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_tenant_admin_ownership(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_tenant_admin_ownership(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_tenant_admin_ownership(payload)

    result: TenantAdminOwnershipCSPResult = mock_azure.create_tenant_admin_ownership(
        payload
    )

    assert result.admin_owner_assignment_id == "id"


def test_create_tenant_principal_ownership(
    mock_azure: AzureCloudProvider, mock_http_error_response
):
    mock_result = mock_requests_response(json_data={"id": "id"})

    mock_azure.sdk.requests.put.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = TenantPrincipalOwnershipCSPPayload(
        **{
            "tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
            "principal_id": "971efe4d-1e80-4e39-b3b9-4e5c63ad446d",
        }
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_tenant_principal_ownership(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_tenant_principal_ownership(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_tenant_principal_ownership(payload)

    result: TenantPrincipalOwnershipCSPResult = mock_azure.create_tenant_principal_ownership(
        payload
    )

    assert result.principal_owner_assignment_id == "id"


def test_create_principal_admin_role(
    mock_azure: AzureCloudProvider, mock_http_error_response
):

    mock_result = mock_requests_response(json_data={"id": "id"})

    mock_azure.sdk.requests.post.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = PrincipalAdminRoleCSPPayload(
        **{
            "tenant_id": uuid4().hex,
            "principal_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
            "admin_role_def_id": uuid4().hex,
        }
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_principal_admin_role(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_principal_admin_role(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_principal_admin_role(payload)

    result: PrincipalAdminRoleCSPResult = mock_azure.create_principal_admin_role(
        payload
    )

    assert result.principal_assignment_id == "id"


def test_create_subscription_creation(
    mock_azure: AzureCloudProvider, mock_http_error_response
):

    mock_result = mock_requests_response(
        status=202, headers={"Location": "https://verify.me", "Retry-After": 10}
    )

    mock_azure.sdk.requests.put.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    management_group_id = str(uuid4())
    payload = SubscriptionCreationCSPPayload(
        **dict(
            tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
            display_name="application_env_sub1",
            parent_group_id=management_group_id,
            billing_account_name="7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31",
            billing_profile_name="KQWI-W2SU-BG7-TGB",
            invoice_section_name="6HMZ-2HLO-PJA-TGB",
        )
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_subscription_creation(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_subscription_creation(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_subscription_creation(payload)

    result: SubscriptionCreationCSPResult = mock_azure.create_subscription_creation(
        payload
    )

    assert result.subscription_verify_url == "https://verify.me"


def test_create_subscription_verification(
    mock_azure: AzureCloudProvider, mock_http_error_response
):

    mock_result = mock_requests_response(
        json_data={
            "subscriptionLink": "/subscriptions/60fbbb72-0516-4253-ab18-c92432ba3230"
        }
    )

    mock_azure.sdk.requests.get.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = SubscriptionVerificationCSPPayload(
        **dict(
            tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
            subscription_verify_url="https://verify.me",
        )
    )
    with pytest.raises(ConnectionException):
        mock_azure.create_subscription_verification(payload)
    with pytest.raises(ConnectionException):
        mock_azure.create_subscription_verification(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.create_subscription_verification(payload)

    result: SuscriptionVerificationCSPResult = mock_azure.create_subscription_verification(
        payload
    )
    assert result.subscription_id == "60fbbb72-0516-4253-ab18-c92432ba3230"


def test_get_reporting_data(mock_azure: AzureCloudProvider, mock_http_error_response):
    mock_result = mock_requests_response(
        json_data={
            "eTag": None,
            "id": "providers/Microsoft.Billing/billingAccounts/52865e4c-52e8-5a6c-da6b-c58f0814f06f:7ea5de9d-b8ce-4901-b1c5-d864320c7b03_2019-05-31/billingProfiles/XQDJ-6LB4-BG7-TGB/invoiceSections/P73M-XC7J-PJA-TGB/providers/Microsoft.CostManagement/query/e82d0cda-2ffb-4476-a98a-425c83c216f9",
            "location": None,
            "name": "e82d0cda-2ffb-4476-a98a-425c83c216f9",
            "properties": {
                "columns": [
                    {"name": "PreTaxCost", "type": "Number"},
                    {"name": "UsageDate", "type": "Number"},
                    {"name": "InvoiceId", "type": "String"},
                    {"name": "Currency", "type": "String"},
                ],
                "nextLink": None,
                "rows": [],
            },
            "sku": None,
            "type": "Microsoft.CostManagement/query",
        }
    )

    mock_azure.sdk.requests.post.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    # Subset of a profile's CSP data that we care about for reporting
    csp_data = {
        "tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
        "billing_profile_properties": {
            "invoice_sections": [
                {
                    "invoice_section_id": "providers/Microsoft.Billing/billingAccounts/52865e4c-52e8-5a6c-da6b-c58f0814f06f:7ea5de9d-b8ce-4901-b1c5-d864320c7b03_2019-05-31/billingProfiles/XQDJ-6LB4-BG7-TGB/invoiceSections/P73M-XC7J-PJA-TGB",
                }
            ],
        },
    }
    payload = CostManagementQueryCSPPayload(
        from_date=pendulum.now().subtract(years=1).add(days=1).format("YYYY-MM-DD"),
        to_date=pendulum.now().format("YYYY-MM-DD"),
        **csp_data,
    )
    with pytest.raises(ConnectionException):
        mock_azure.get_reporting_data(payload)
    with pytest.raises(ConnectionException):
        mock_azure.get_reporting_data(payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure.get_reporting_data(payload)

    data: CostManagementQueryCSPResult = mock_azure.get_reporting_data(payload)

    assert isinstance(data, CostManagementQueryCSPResult)
    assert data.name == "e82d0cda-2ffb-4476-a98a-425c83c216f9"
    assert len(data.properties.columns) == 4


def test_get_reporting_data_malformed_payload(mock_azure: AzureCloudProvider):
    mock_result = mock_requests_response()

    mock_azure.sdk.requests.post.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    # Malformed csp_data payloads that should throw pydantic validation errors
    index_error = {
        "tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
        "billing_profile_properties": {"invoice_sections": [],},
    }
    key_error = {
        "tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
        "billing_profile_properties": {"invoice_sections": [{}],},
    }

    for malformed_payload in [key_error, index_error]:
        with pytest.raises(pydantic.ValidationError):
            assert mock_azure.get_reporting_data(
                CostManagementQueryCSPPayload(
                    from_date="foo", to_date="bar", **malformed_payload,
                )
            )


def test_get_keyvault_token(mock_http_error_response, unmocked_cloud_provider):
    cloud_provider = unmocked_cloud_provider
    mock_result = mock_requests_response(
        status=200,
        json_data={
            "token_type": "Bearer",
            "expires_in": "3599",
            "ext_expires_in": "3599",
            "expires_on": "1588197654",
            "not_before": "1588193754",
            "resource": f"https://{cloud_provider.sdk.cloud.suffixes.keyvault_dns[1:]}",
            "access_token": "TOKEN",
        },
    )

    cloud_provider.sdk.requests.get = Mock()
    cloud_provider.sdk.requests.get.side_effect = [
        cloud_provider.sdk.requests.exceptions.ConnectionError,
        cloud_provider.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]
    with pytest.raises(ConnectionException):
        cloud_provider._get_keyvault_token()
    with pytest.raises(ConnectionException):
        cloud_provider._get_keyvault_token()
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        cloud_provider._get_keyvault_token()

    result = cloud_provider._get_keyvault_token()
    assert result == "TOKEN"


def test_get_secret(unmocked_cloud_provider, mock_http_error_response):
    cloud_provider = unmocked_cloud_provider
    mock_result = mock_requests_response(
        status=200,
        json_data={
            "value": "mytestvalue",
            "id": "https://hybridcz-pwdev-keyvault.vault.azure.net/secrets/testsecret/abc123",
            "attributes": {
                "enabled": True,
                "created": 1588096321,
                "updated": 1588096321,
                "recoveryLevel": "Recoverable+Purgeable",
            },
        },
    )

    cloud_provider._get_keyvault_token = Mock(return_value="TOKEN")
    cloud_provider.sdk.requests.get = Mock()
    cloud_provider.sdk.requests.get.side_effect = [
        cloud_provider.sdk.requests.exceptions.ConnectionError,
        cloud_provider.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]
    with pytest.raises(ConnectionException):
        cloud_provider.get_secret("secret key")
    with pytest.raises(ConnectionException):
        cloud_provider.get_secret("secret key")
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        cloud_provider.get_secret("secret key")

    result = cloud_provider.get_secret("secret key")
    assert result == "mytestvalue"


def test_set_secret(unmocked_cloud_provider, mock_http_error_response):
    cloud_provider = unmocked_cloud_provider
    response_id = (
        f"{cloud_provider.config.get('AZURE_VAULT_URL')}secrets/testsecret/abc123"
    )
    mock_result = mock_requests_response(
        status=200,
        json_data={
            "value": "mytestvalue",
            "id": response_id,
            "attributes": {
                "enabled": True,
                "created": 1588096321,
                "updated": 1588096321,
                "recoveryLevel": "Recoverable+Purgeable",
            },
        },
    )

    cloud_provider._get_keyvault_token = Mock(return_value="TOKEN")
    cloud_provider.sdk.requests.put = Mock()
    cloud_provider.sdk.requests.put.side_effect = [
        cloud_provider.sdk.requests.exceptions.ConnectionError,
        cloud_provider.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]
    with pytest.raises(ConnectionException):
        cloud_provider.set_secret("secret key", "mytestvalue")
    with pytest.raises(ConnectionException):
        cloud_provider.set_secret("secret key", "mytestvalue")
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        cloud_provider.set_secret("secret key", "mytestvalue")

    result = cloud_provider.set_secret("secret key", "mytestvalue")
    assert result["id"] == response_id


def test_create_active_directory_user(
    mock_azure: AzureCloudProvider, mock_http_error_response
):
    mock_result = mock_requests_response(json_data={"id": "id"})

    mock_azure.sdk.requests.post.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]

    payload = UserCSPPayload(
        tenant_id=uuid4().hex,
        display_name="Test Testerson",
        tenant_host_name="testtenant",
        email="test@testerson.test",
        password="asdfghjkl",  # pragma: allowlist secret
    )
    with pytest.raises(ConnectionException):
        mock_azure._create_active_directory_user("token", payload)
    with pytest.raises(ConnectionException):
        mock_azure._create_active_directory_user("token", payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure._create_active_directory_user("token", payload)

    result = mock_azure._create_active_directory_user("token", payload)

    assert result.id == "id"


def test_update_active_directory_user_email(
    mock_azure: AzureCloudProvider, mock_http_error_response
):
    mock_result = mock_requests_response()

    mock_azure.sdk.requests.patch.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]
    payload = UserCSPPayload(
        tenant_id=uuid4().hex,
        display_name="Test Testerson",
        tenant_host_name="testtenant",
        email="test@testerson.test",
        password="asdfghjkl",  # pragma: allowlist secret
    )
    with pytest.raises(ConnectionException):
        mock_azure._update_active_directory_user_email("token", uuid4().hex, payload)
    with pytest.raises(ConnectionException):
        mock_azure._update_active_directory_user_email("token", uuid4().hex, payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure._update_active_directory_user_email("token", uuid4().hex, payload)

    result = mock_azure._update_active_directory_user_email(
        "token", uuid4().hex, payload
    )

    assert result


def test_update_active_directory_user_password_profile(
    mock_azure: AzureCloudProvider, mock_http_error_response
):
    mock_result = mock_requests_response()

    mock_azure.sdk.requests.patch.side_effect = [
        mock_azure.sdk.requests.exceptions.ConnectionError,
        mock_azure.sdk.requests.exceptions.Timeout,
        mock_http_error_response,
        mock_result,
    ]
    payload = TenantAdminCredentialResetCSPPayload(
        tenant_id="6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
        user_object_id="acf1c3bb-2b64-4f74-8689-fb6521ae10f8",
        new_password="asdfghjkl",  # pragma: allowlist secret
    )
    with pytest.raises(ConnectionException):
        mock_azure._update_active_directory_user_password_profile("token", payload)
    with pytest.raises(ConnectionException):
        mock_azure._update_active_directory_user_password_profile("token", payload)
    with pytest.raises(UnknownServerException, match=r".*500 Server Error.*"):
        mock_azure._update_active_directory_user_password_profile("token", payload)

    result = mock_azure._update_active_directory_user_password_profile("token", payload)

    assert result


def test_create_user(mock_azure: AzureCloudProvider):
    class AuthenticaionContext(object):
        def __init__(*a, **kw):
            pass

        def acquire_token_with_client_credentials(*a, **kw):
            return {"accessToken": "foo"}

    mock_azure.sdk.adal.AuthenticationContext = AuthenticaionContext
    mock_user_invite = mock_requests_response(json_data={"invitedUser": {"id": "id"}})
    mock_azure.sdk.requests.post.return_value = mock_user_invite

    payload = UserCSPPayload(
        tenant_id=uuid4().hex,
        display_name="Test Testerson",
        tenant_host_name="testtenant",
        email="test@testerson.test",
        password="asdfghjkl",  # pragma: allowlist secret
    )

    result = mock_azure.create_user(payload)
    assert result.id == "id"


def test_create_user_role(mock_azure: AzureCloudProvider):

    mock_result_create = mock_requests_response(json_data={"id": "id"})
    mock_azure.sdk.requests.put.return_value = mock_result_create

    payload = UserRoleCSPPayload(
        tenant_id=uuid4().hex,
        user_object_id=str(uuid4()),
        management_group_id=str(uuid4()),
        role="owner",
    )

    result = mock_azure.create_user_role(payload)

    assert result.id == "id"


def test_create_user_role_failure(mock_azure: AzureCloudProvider):

    mock_result_create = mock_requests_response(ok=False)
    mock_azure.sdk.requests.put.return_value = mock_result_create

    payload = UserRoleCSPPayload(
        tenant_id=uuid4().hex,
        user_object_id=str(uuid4()),
        management_group_id=str(uuid4()),
        role="owner",
    )

    with pytest.raises(UserProvisioningException):
        mock_azure.create_user_role(payload)


def test_create_billing_owner(mock_azure: AzureCloudProvider):

    final_result = "1-2-3"

    # create_billing_owner does: POST, PATCH, GET, POST

    # mock POST so that it pops off results in the order we want
    mock_azure.sdk.requests.post.side_effect = [
        mock_requests_response(json_data={"id": final_result}),
        mock_requests_response(),
    ]
    # return value for PATCH doesn't matter much
    mock_azure.sdk.requests.patch.return_value = mock_requests_response()
    # return value for GET needs to be a JSON object with a list of role definitions
    mock_azure.sdk.requests.get.return_value = mock_requests_response(
        json_data={"value": [{"displayName": "Billing Administrator", "id": "4567"}]}
    )

    payload = BillingOwnerCSPPayload(
        tenant_id=uuid4().hex,
        domain_name="rebelalliance",
        password_recovery_email_address="many@bothans.org",
    )

    result = mock_azure.create_billing_owner(payload)
    assert result.billing_owner_id == final_result


def test_update_tenant_creds(mock_azure: AzureCloudProvider, monkeypatch):

    existing_secrets = {
        "tenant_id": "mytenant",
        "tenant_admin_username": "admin",
        "tenant_admin_password": "foo",  # pragma: allowlist secret
    }
    new_secrets = {
        "tenant_id": str(uuid4()),
        "tenant_sp_client_id": str(uuid4()),
        "tenant_sp_key": "1234",
    }
    monkeypatch.setattr(
        mock_azure, "get_secret", Mock(return_value=json.dumps(existing_secrets)),
    )

    mock_new_secrets = KeyVaultCredentials(**new_secrets)
    updated_secret = mock_azure.update_tenant_creds("mytenant", mock_new_secrets)

    assert updated_secret == KeyVaultCredentials(**{**existing_secrets, **new_secrets})


class TestGetCalculatorCreds:
    def test_get_calculator_creds_succeeds(self, mock_azure: AzureCloudProvider):
        assert mock_azure._get_calculator_creds() == MOCK_ACCESS_TOKEN

    def test_get_calculator_creds_fails(self, mock_azure: AzureCloudProvider):
        mock_azure.sdk.adal.AuthenticationContext.return_value.acquire_token_with_client_credentials.side_effect = AdalError(
            "Adal Error"
        )
        with pytest.raises(AuthenticationException):
            mock_azure._get_calculator_creds()


def test_get_calculator_url(mock_azure: AzureCloudProvider):
    assert (
        mock_azure.get_calculator_url()
        == f"{mock_azure.config.get('AZURE_CALC_URL')}?access_token={MOCK_ACCESS_TOKEN}"
    )


class TestGenerateValidDomainName:
    def test_success(self, mock_azure: AzureCloudProvider):
        tenant_name = "tenant"
        assert mock_azure.generate_valid_domain_name(tenant_name) == tenant_name

    def test_failure_after_max_tries(self, monkeypatch, mock_azure: AzureCloudProvider):
        monkeypatch.setattr(
            "atat.domain.csp.cloud.AzureCloudProvider.validate_domain_name",
            Mock(return_value=False),
        )
        with pytest.raises(DomainNameException):
            mock_azure.generate_valid_domain_name(name="test", max_tries=3)

    def test_unique(self, monkeypatch, mock_azure: AzureCloudProvider):
        # mock that a tenant exists with the name tenant_name
        tenant_name = "tenant"

        def _validate_domain_name(mock_azure, name):
            if name == tenant_name:
                return False
            else:
                return True

        monkeypatch.setattr(
            "atat.domain.csp.cloud.AzureCloudProvider.validate_domain_name",
            _validate_domain_name,
        )
        assert mock_azure.generate_valid_domain_name(tenant_name) != tenant_name


def test_create_policies(mock_azure: AzureCloudProvider, monkeypatch):
    final_assignment_id = "whatever"
    put_results = [
        mock_requests_response(
            json_data={"id": "foo", "properties": {"displayName": "foo"}}, status=201
        ),
        mock_requests_response(
            json_data={"id": "bar", "properties": {"displayName": "bar"}}, status=201
        ),
        mock_requests_response(
            json_data={"id": "baz", "properties": {"displayName": "baz"}}, status=201
        ),
        mock_requests_response(
            json_data={
                "id": "test_id",
                "policyType": "Custom",
                "name": "test_name",
                "properties": {"displayName": "test_display_name"},
            },
            status=201,
        ),
        mock_requests_response(json_data={"id": final_assignment_id}, status=201),
    ]
    mock_session = Mock
    mock_session.put = Mock(side_effect=put_results)
    monkeypatch.setattr("requests.Session", mock_session)

    payload = PoliciesCSPPayload(
        tenant_id="1234", root_management_group_name=str(uuid4()),
    )
    result: PoliciesCSPResult = mock_azure.create_policies(payload)
    assert result.policy_assignment_id == final_assignment_id


def test_get_service_principal_token_fails(mock_azure: AzureCloudProvider):
    mock_azure.sdk.adal.AuthenticationContext.return_value.acquire_token_with_client_credentials.side_effect = AdalError(
        "Adal Error"
    )
    with pytest.raises(AuthenticationException):
        mock_azure._get_service_principal_token("resource", "client", "secret")


def test_get_user_principal_token_for_resource_fails(mock_azure: AzureCloudProvider):
    mock_azure.sdk.adal.AuthenticationContext.return_value.acquire_token_with_username_password.side_effect = AdalError(
        "Adal Error"
    )
    with pytest.raises(AuthenticationException):
        mock_azure._get_user_principal_token_for_resource(
            "username", "password", "tenant_id", "my_resource"
        )
