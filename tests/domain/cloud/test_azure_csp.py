import json
from unittest.mock import Mock, patch
from uuid import uuid4

import pendulum
import pydantic
import pytest
from tests.factories import ApplicationFactory, EnvironmentFactory
from tests.mock_azure import AUTH_CREDENTIALS, mock_azure

from atst.domain.csp.cloud import AzureCloudProvider
from atst.domain.csp.cloud.models import (
    AdminRoleDefinitionCSPPayload,
    AdminRoleDefinitionCSPResult,
    ApplicationCSPPayload,
    ApplicationCSPResult,
    BillingInstructionCSPPayload,
    BillingInstructionCSPResult,
    BillingProfileCreationCSPPayload,
    BillingProfileCreationCSPResult,
    BillingProfileTenantAccessCSPPayload,
    BillingProfileTenantAccessCSPResult,
    BillingProfileVerificationCSPPayload,
    BillingProfileVerificationCSPResult,
    CostManagementQueryCSPResult,
    EnvironmentCSPPayload,
    EnvironmentCSPResult,
    PrincipalAdminRoleCSPPayload,
    PrincipalAdminRoleCSPResult,
    ProductPurchaseCSPPayload,
    ProductPurchaseCSPResult,
    ProductPurchaseVerificationCSPPayload,
    ProductPurchaseVerificationCSPResult,
    ReportingCSPPayload,
    SubscriptionCreationCSPPayload,
    SubscriptionCreationCSPResult,
    SubscriptionVerificationCSPPayload,
    SuscriptionVerificationCSPResult,
    TaskOrderBillingCreationCSPPayload,
    TaskOrderBillingCreationCSPResult,
    TaskOrderBillingVerificationCSPPayload,
    TaskOrderBillingVerificationCSPResult,
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
)

BILLING_ACCOUNT_NAME = "52865e4c-52e8-5a6c-da6b-c58f0814f06f:7ea5de9d-b8ce-4901-b1c5-d864320c7b03_2019-05-31"


def mock_management_group_create(mock_azure, spec_dict):
    mock_azure.sdk.managementgroups.ManagementGroupsAPI.return_value.management_groups.create_or_update.return_value.result.return_value = (
        spec_dict
    )


def test_create_environment_succeeds(mock_azure: AzureCloudProvider):
    environment = EnvironmentFactory.create()
    mock_management_group_create(mock_azure, {"id": "Test Id"})

    mock_azure = mock_get_secret(mock_azure)

    payload = EnvironmentCSPPayload(
        tenant_id="1234", display_name=environment.name, parent_id=str(uuid4())
    )
    result = mock_azure.create_environment(payload)

    assert result.id == "Test Id"


# mock the get_secret so it returns a JSON string
MOCK_CREDS = {
    "tenant_id": str(uuid4()),
    "tenant_sp_client_id": str(uuid4()),
    "tenant_sp_key": "1234",
}


def mock_get_secret(azure, val=None):
    if val is None:
        val = json.dumps(MOCK_CREDS)
    azure.get_secret = lambda *a, **k: val

    return azure


def test_create_application_succeeds(mock_azure: AzureCloudProvider):
    application = ApplicationFactory.create()
    mock_management_group_create(mock_azure, {"id": "Test Id"})
    mock_azure = mock_get_secret(mock_azure)

    payload = ApplicationCSPPayload(
        tenant_id="1234", display_name=application.name, parent_id=str(uuid4())
    )

    result: ApplicationCSPResult = mock_azure.create_application(payload)

    assert result.id == "Test Id"


def test_create_policy_definition_succeeds(mock_azure: AzureCloudProvider):
    subscription_id = str(uuid4())
    management_group_id = str(uuid4())
    properties = {
        "policyType": "test",
        "displayName": "test policy",
    }

    result = mock_azure._create_policy_definition(
        AUTH_CREDENTIALS, subscription_id, management_group_id, properties
    )
    azure_sdk_method = (
        mock_azure.sdk.policy.PolicyClient.return_value.policy_definitions.create_or_update_at_management_group
    )
    mock_policy_definition = (
        mock_azure.sdk.policy.PolicyClient.return_value.policy_definitions.models.PolicyDefinition()
    )
    assert azure_sdk_method.called
    azure_sdk_method.assert_called_with(
        management_group_id=management_group_id,
        policy_definition_name=properties.get("displayName"),
        parameters=mock_policy_definition,
    )


def test_create_tenant(mock_azure: AzureCloudProvider):
    mock_result = Mock()
    mock_result.json.return_value = {
        "objectId": "0a5f4926-e3ee-4f47-a6e3-8b0a30a40e3d",
        "tenantId": "60ff9d34-82bf-4f21-b565-308ef0533435",
        "userId": "1153801116406515559",
    }
    mock_result.status_code = 200
    mock_azure.sdk.requests.post.return_value = mock_result
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
    mock_azure = mock_get_secret(mock_azure)
    result = mock_azure.create_tenant(payload)
    body: TenantCSPResult = result.get("body")
    assert body.tenant_id == "60ff9d34-82bf-4f21-b565-308ef0533435"


def test_create_tenant_fails(mock_azure: AzureCloudProvider):
    mock_result = Mock()
    mock_result.json.return_value = {"error": "body"}
    mock_result.status_code = 403
    mock_azure.sdk.requests.post.return_value = mock_result
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
    mock_azure = mock_get_secret(mock_azure)
    result = mock_azure.create_tenant(payload)
    assert result.get("status") == "error"


def test_create_billing_profile_creation(mock_azure: AzureCloudProvider):
    mock_azure.sdk.adal.AuthenticationContext.return_value.context.acquire_token_with_client_credentials.return_value = {
        "accessToken": "TOKEN"
    }

    mock_result = Mock()
    mock_result.headers = {
        "Location": "http://retry-url",
        "Retry-After": "10",
    }
    mock_result.status_code = 202
    mock_azure.sdk.requests.post.return_value = mock_result
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
    result = mock_azure.create_billing_profile_creation(payload)
    body: BillingProfileCreationCSPResult = result.get("body")
    assert body.billing_profile_retry_after == 10


def test_validate_billing_profile_creation(mock_azure: AzureCloudProvider):
    mock_azure.sdk.adal.AuthenticationContext.return_value.context.acquire_token_with_client_credentials.return_value = {
        "accessToken": "TOKEN"
    }

    mock_result = Mock()
    mock_result.status_code = 200
    mock_result.json.return_value = {
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
                    "properties": {"displayName": "First Portfolio Billing Profile"},
                    "type": "Microsoft.Billing/billingAccounts/billingProfiles/invoiceSections",
                }
            ],
        },
        "type": "Microsoft.Billing/billingAccounts/billingProfiles",
    }
    mock_azure.sdk.requests.get.return_value = mock_result

    payload = BillingProfileVerificationCSPPayload(
        **dict(
            tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
            billing_profile_verify_url="https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/createBillingProfile_478d5706-71f9-4a8b-8d4e-2cbaca27a668?api-version=2019-10-01-preview",
        )
    )

    result = mock_azure.create_billing_profile_verification(payload)
    body: BillingProfileVerificationCSPResult = result.get("body")
    assert body.billing_profile_name == "KQWI-W2SU-BG7-TGB"
    assert (
        body.billing_profile_properties.billing_profile_display_name
        == "First Portfolio Billing Profile"
    )


def test_create_billing_profile_tenant_access(mock_azure: AzureCloudProvider):
    mock_azure.sdk.adal.AuthenticationContext.return_value.context.acquire_token_with_client_credentials.return_value = {
        "accessToken": "TOKEN"
    }

    mock_result = Mock()
    mock_result.status_code = 201
    mock_result.json.return_value = {
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
    }

    mock_azure.sdk.requests.post.return_value = mock_result

    payload = BillingProfileTenantAccessCSPPayload(
        **dict(
            tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
            user_object_id="0a5f4926-e3ee-4f47-a6e3-8b0a30a40e3d",
            billing_account_name="7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31",
            billing_profile_name="KQWI-W2SU-BG7-TGB",
        )
    )

    result = mock_azure.create_billing_profile_tenant_access(payload)
    body: BillingProfileTenantAccessCSPResult = result.get("body")
    assert (
        body.billing_role_assignment_name
        == "40000000-aaaa-bbbb-cccc-100000000000_0a5f4926-e3ee-4f47-a6e3-8b0a30a40e3d"
    )


def test_create_task_order_billing_creation(mock_azure: AzureCloudProvider):
    mock_azure.sdk.adal.AuthenticationContext.return_value.context.acquire_token_with_client_credentials.return_value = {
        "accessToken": "TOKEN"
    }

    mock_result = Mock()
    mock_result.status_code = 202
    mock_result.headers = {
        "Location": "https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/patchBillingProfile_KQWI-W2SU-BG7-TGB:02715576-4118-466c-bca7-b1cd3169ff46?api-version=2019-10-01-preview",
        "Retry-After": "10",
    }

    mock_azure.sdk.requests.patch.return_value = mock_result

    payload = TaskOrderBillingCreationCSPPayload(
        **dict(
            tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
            billing_account_name="7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31",
            billing_profile_name="KQWI-W2SU-BG7-TGB",
        )
    )

    result = mock_azure.create_task_order_billing_creation(payload)
    body: TaskOrderBillingCreationCSPResult = result.get("body")

    assert (
        body.task_order_billing_verify_url
        == "https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/patchBillingProfile_KQWI-W2SU-BG7-TGB:02715576-4118-466c-bca7-b1cd3169ff46?api-version=2019-10-01-preview"
    )


def test_create_task_order_billing_verification(mock_azure):
    mock_azure.sdk.adal.AuthenticationContext.return_value.context.acquire_token_with_client_credentials.return_value = {
        "accessToken": "TOKEN"
    }

    mock_result = Mock()
    mock_result.status_code = 200
    mock_result.json.return_value = {
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
    mock_azure.sdk.requests.get.return_value = mock_result

    payload = TaskOrderBillingVerificationCSPPayload(
        **dict(
            tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
            task_order_billing_verify_url="https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/createBillingProfile_478d5706-71f9-4a8b-8d4e-2cbaca27a668?api-version=2019-10-01-preview",
        )
    )

    result = mock_azure.create_task_order_billing_verification(payload)
    body: TaskOrderBillingVerificationCSPResult = result.get("body")
    assert body.billing_profile_name == "KQWI-W2SU-BG7-TGB"
    assert (
        body.billing_profile_enabled_plan_details.enabled_azure_plans[0].get("skuId")
        == "0001"
    )


def test_create_billing_instruction(mock_azure: AzureCloudProvider):
    mock_azure.sdk.adal.AuthenticationContext.return_value.context.acquire_token_with_client_credentials.return_value = {
        "accessToken": "TOKEN"
    }

    mock_result = Mock()
    mock_result.status_code = 200
    mock_result.json.return_value = {
        "name": "TO1:CLIN001",
        "properties": {
            "amount": 1000.0,
            "endDate": "2020-03-01T00:00:00+00:00",
            "startDate": "2020-01-01T00:00:00+00:00",
        },
        "type": "Microsoft.Billing/billingAccounts/billingProfiles/billingInstructions",
    }

    mock_azure.sdk.requests.put.return_value = mock_result

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
    result = mock_azure.create_billing_instruction(payload)
    body: BillingInstructionCSPResult = result.get("body")
    assert body.reported_clin_name == "TO1:CLIN001"


def test_create_product_purchase(mock_azure: AzureCloudProvider):
    mock_azure.sdk.adal.AuthenticationContext.return_value.context.acquire_token_with_client_credentials.return_value = {
        "accessToken": "TOKEN"
    }

    mock_result = Mock()
    mock_result.status_code = 202
    mock_result.headers = {
        "Location": "https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/patchBillingProfile_KQWI-W2SU-BG7-TGB:02715576-4118-466c-bca7-b1cd3169ff46?api-version=2019-10-01-preview",
        "Retry-After": "10",
    }

    mock_azure.sdk.requests.post.return_value = mock_result

    payload = ProductPurchaseCSPPayload(
        **dict(
            tenant_id="6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
            billing_account_name="7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31",
            billing_profile_name="KQWI-W2SU-BG7-TGB",
        )
    )

    result = mock_azure.create_product_purchase(payload)
    body: ProductPurchaseCSPResult = result.get("body")
    assert (
        body.product_purchase_verify_url
        == "https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/patchBillingProfile_KQWI-W2SU-BG7-TGB:02715576-4118-466c-bca7-b1cd3169ff46?api-version=2019-10-01-preview"
    )


def test_create_product_purchase_verification(mock_azure):
    mock_azure.sdk.adal.AuthenticationContext.return_value.context.acquire_token_with_client_credentials.return_value = {
        "accessToken": "TOKEN"
    }

    mock_result = Mock()
    mock_result.status_code = 200
    mock_result.json.return_value = {
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

    mock_azure.sdk.requests.get.return_value = mock_result

    payload = ProductPurchaseVerificationCSPPayload(
        **dict(
            tenant_id="6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
            product_purchase_verify_url="https://management.azure.com/providers/Microsoft.Billing/billingAccounts/7c89b735-b22b-55c0-ab5a-c624843e8bf6:de4416ce-acc6-44b1-8122-c87c4e903c91_2019-05-31/operationResults/createBillingProfile_478d5706-71f9-4a8b-8d4e-2cbaca27a668?api-version=2019-10-01-preview",
        )
    )

    result = mock_azure.create_product_purchase_verification(payload)
    body: ProductPurchaseVerificationCSPResult = result.get("body")
    assert body.premium_purchase_date == "01/31/2020"


def test_create_tenant_principal_app(mock_azure: AzureCloudProvider):
    with patch.object(
        AzureCloudProvider,
        "_get_elevated_management_token",
        wraps=mock_azure._get_elevated_management_token,
    ) as get_elevated_management_token:
        get_elevated_management_token.return_value = "my fake token"

        mock_result = Mock()
        mock_result.ok = True
        mock_result.json.return_value = {"appId": "appId", "id": "id"}

        mock_azure.sdk.requests.post.return_value = mock_result
        mock_azure = mock_get_secret(mock_azure)

        payload = TenantPrincipalAppCSPPayload(
            **{"tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4"}
        )
        result: TenantPrincipalAppCSPResult = mock_azure.create_tenant_principal_app(
            payload
        )

        assert result.principal_app_id == "appId"


def test_create_tenant_principal(mock_azure: AzureCloudProvider):
    with patch.object(
        AzureCloudProvider,
        "_get_elevated_management_token",
        wraps=mock_azure._get_elevated_management_token,
    ) as get_elevated_management_token:
        get_elevated_management_token.return_value = "my fake token"

        mock_result = Mock()
        mock_result.ok = True
        mock_result.json.return_value = {"id": "principal_id"}

        mock_azure.sdk.requests.post.return_value = mock_result
        mock_azure = mock_get_secret(mock_azure)

        payload = TenantPrincipalCSPPayload(
            **{
                "tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
                "principal_app_id": "appId",
            }
        )

        result: TenantPrincipalCSPResult = mock_azure.create_tenant_principal(payload)

        assert result.principal_id == "principal_id"


def test_create_tenant_principal_credential(mock_azure: AzureCloudProvider):
    with patch.object(
        AzureCloudProvider,
        "_get_elevated_management_token",
        wraps=mock_azure._get_elevated_management_token,
    ) as get_elevated_management_token:
        get_elevated_management_token.return_value = "my fake token"

        mock_result = Mock()
        mock_result.ok = True
        mock_result.json.return_value = {"secretText": "new secret key"}

        mock_azure.sdk.requests.post.return_value = mock_result

        mock_azure = mock_get_secret(mock_azure)

        payload = TenantPrincipalCredentialCSPPayload(
            **{
                "tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
                "principal_app_id": "appId",
                "principal_app_object_id": "appObjId",
            }
        )

        result: TenantPrincipalCredentialCSPResult = mock_azure.create_tenant_principal_credential(
            payload
        )

        assert result.principal_creds_established == True


def test_create_admin_role_definition(mock_azure: AzureCloudProvider):
    with patch.object(
        AzureCloudProvider,
        "_get_tenant_admin_token",
        wraps=mock_azure._get_tenant_admin_token,
    ) as get_tenant_admin_token:
        get_tenant_admin_token.return_value = "my fake token"

        mock_result = Mock()
        mock_result.ok = True
        mock_result.json.return_value = {
            "value": [
                {"id": "wrongid", "displayName": "Wrong Role"},
                {"id": "id", "displayName": "Company Administrator"},
            ]
        }

        mock_azure.sdk.requests.get.return_value = mock_result
        mock_azure = mock_get_secret(mock_azure)

        payload = AdminRoleDefinitionCSPPayload(
            **{"tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4"}
        )

        result: AdminRoleDefinitionCSPResult = mock_azure.create_admin_role_definition(
            payload
        )

        assert result.admin_role_def_id == "id"


def test_create_tenant_admin_ownership(mock_azure: AzureCloudProvider):
    with patch.object(
        AzureCloudProvider,
        "_get_elevated_management_token",
        wraps=mock_azure._get_elevated_management_token,
    ) as get_elevated_management_token:
        get_elevated_management_token.return_value = "my fake token"

        mock_result = Mock()
        mock_result.ok = True
        mock_result.json.return_value = {"id": "id"}

        mock_azure.sdk.requests.put.return_value = mock_result

        payload = TenantAdminOwnershipCSPPayload(
            **{
                "tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
                "user_object_id": "971efe4d-1e80-4e39-b3b9-4e5c63ad446d",
            }
        )

        result: TenantAdminOwnershipCSPResult = mock_azure.create_tenant_admin_ownership(
            payload
        )

        assert result.admin_owner_assignment_id == "id"


def test_create_tenant_principal_ownership(mock_azure: AzureCloudProvider):
    with patch.object(
        AzureCloudProvider,
        "_get_elevated_management_token",
        wraps=mock_azure._get_elevated_management_token,
    ) as get_elevated_management_token:
        get_elevated_management_token.return_value = "my fake token"

        mock_result = Mock()
        mock_result.ok = True
        mock_result.json.return_value = {"id": "id"}

        mock_azure.sdk.requests.put.return_value = mock_result

        payload = TenantPrincipalOwnershipCSPPayload(
            **{
                "tenant_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
                "principal_id": "971efe4d-1e80-4e39-b3b9-4e5c63ad446d",
            }
        )

        result: TenantPrincipalOwnershipCSPResult = mock_azure.create_tenant_principal_ownership(
            payload
        )

        assert result.principal_owner_assignment_id == "id"


def test_create_principal_admin_role(mock_azure: AzureCloudProvider):
    with patch.object(
        AzureCloudProvider,
        "_get_tenant_admin_token",
        wraps=mock_azure._get_tenant_admin_token,
    ) as get_tenant_admin_token:
        get_tenant_admin_token.return_value = "my fake token"

        mock_result = Mock()
        mock_result.ok = True
        mock_result.json.return_value = {"id": "id"}

        mock_azure.sdk.requests.post.return_value = mock_result

        payload = PrincipalAdminRoleCSPPayload(
            **{
                "tenant_id": uuid4().hex,
                "principal_id": "6d2d2d6c-a6d6-41e1-8bb1-73d11475f8f4",
                "admin_role_def_id": uuid4().hex,
            }
        )

        result: PrincipalAdminRoleCSPResult = mock_azure.create_principal_admin_role(
            payload
        )

        assert result.principal_assignment_id == "id"


def test_create_subscription_creation(mock_azure: AzureCloudProvider):
    with patch.object(
        AzureCloudProvider,
        "_get_tenant_principal_token",
        wraps=mock_azure._get_tenant_principal_token,
    ) as _get_tenant_principal_token:
        _get_tenant_principal_token.return_value = "my fake token"

        mock_result = Mock()
        mock_result.status_code = 202
        mock_result.headers = {
            "Location": "https://verify.me",
            "Retry-After": 10,
        }
        mock_result.json.return_value = {}
        mock_azure.sdk.requests.put.return_value = mock_result
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

        result: SubscriptionCreationCSPResult = mock_azure.create_subscription_creation(
            payload
        )

        assert result.subscription_verify_url == "https://verify.me"


def test_create_subscription_verification(mock_azure: AzureCloudProvider):
    with patch.object(
        AzureCloudProvider,
        "_get_tenant_principal_token",
        wraps=mock_azure._get_tenant_principal_token,
    ) as _get_tenant_principal_token:
        _get_tenant_principal_token.return_value = "my fake token"

        mock_result = Mock()
        mock_result.ok = True
        mock_result.json.return_value = {
            "subscriptionLink": "/subscriptions/60fbbb72-0516-4253-ab18-c92432ba3230"
        }
        mock_azure.sdk.requests.get.return_value = mock_result

        payload = SubscriptionVerificationCSPPayload(
            **dict(
                tenant_id="60ff9d34-82bf-4f21-b565-308ef0533435",
                subscription_verify_url="https://verify.me",
            )
        )

        result: SuscriptionVerificationCSPResult = mock_azure.create_subscription_verification(
            payload
        )
        assert result.subscription_id == "60fbbb72-0516-4253-ab18-c92432ba3230"


def test_get_reporting_data(mock_azure: AzureCloudProvider):
    mock_result = Mock()
    mock_result.json.return_value = {
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
    mock_result.ok = True
    mock_azure.sdk.requests.post.return_value = mock_result
    mock_azure = mock_get_secret(mock_azure)

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

    data: CostManagementQueryCSPResult = mock_azure.get_reporting_data(
        ReportingCSPPayload(
            from_date=pendulum.now().subtract(years=1).add(days=1).format("YYYY-MM-DD"),
            to_date=pendulum.now().format("YYYY-MM-DD"),
            **csp_data,
        )
    )

    assert isinstance(data, CostManagementQueryCSPResult)
    assert data.name == "e82d0cda-2ffb-4476-a98a-425c83c216f9"
    assert len(data.properties.columns) == 4


def test_get_reporting_data_malformed_payload(mock_azure: AzureCloudProvider):
    mock_result = Mock()
    mock_result.ok = True
    mock_azure.sdk.requests.post.return_value = mock_result
    mock_azure = mock_get_secret(mock_azure)

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
                ReportingCSPPayload(
                    from_date="foo", to_date="bar", **malformed_payload,
                )
            )


def test_get_secret(mock_azure: AzureCloudProvider):
    with patch.object(
        AzureCloudProvider,
        "_get_client_secret_credential_obj",
        wraps=mock_azure._get_client_secret_credential_obj,
    ) as _get_client_secret_credential_obj:
        _get_client_secret_credential_obj.return_value = {}

        mock_azure.sdk.secrets.SecretClient.return_value.get_secret.return_value.value = (
            "my secret"
        )

        assert mock_azure.get_secret("secret key") == "my secret"


def test_set_secret(mock_azure: AzureCloudProvider):
    with patch.object(
        AzureCloudProvider,
        "_get_client_secret_credential_obj",
        wraps=mock_azure._get_client_secret_credential_obj,
    ) as _get_client_secret_credential_obj:
        _get_client_secret_credential_obj.return_value = {}

        mock_azure.sdk.secrets.SecretClient.return_value.set_secret.return_value = (
            "my secret"
        )

        assert mock_azure.set_secret("secret key", "secret_value") == "my secret"


def test_create_active_directory_user(mock_azure: AzureCloudProvider):
    mock_result = Mock()
    mock_result.ok = True
    mock_result.json.return_value = {"id": "id"}
    mock_azure.sdk.requests.post.return_value = mock_result

    payload = UserCSPPayload(
        tenant_id=uuid4().hex,
        display_name="Test Testerson",
        tenant_host_name="testtenant",
        email="test@testerson.test",
        password="asdfghjkl",  # pragma: allowlist secret
    )

    result = mock_azure._create_active_directory_user("token", payload)

    assert result.id == "id"


def test_update_active_directory_user_email(mock_azure: AzureCloudProvider):
    mock_result = Mock()
    mock_result.ok = True
    mock_azure.sdk.requests.patch.return_value = mock_result

    payload = UserCSPPayload(
        tenant_id=uuid4().hex,
        display_name="Test Testerson",
        tenant_host_name="testtenant",
        email="test@testerson.test",
        password="asdfghjkl",  # pragma: allowlist secret
    )

    result = mock_azure._update_active_directory_user_email(
        "token", uuid4().hex, payload
    )

    assert result


def test_create_user(mock_azure: AzureCloudProvider):
    with patch.object(
        AzureCloudProvider,
        "_get_tenant_principal_token",
        wraps=mock_azure._get_tenant_principal_token,
    ) as _get_tenant_principal_token:
        _get_tenant_principal_token.return_value = "token"

        mock_result_create = Mock()
        mock_result_create.ok = True
        mock_result_create.json.return_value = {"id": "id"}
        mock_azure.sdk.requests.post.return_value = mock_result_create

        mock_result_update = Mock()
        mock_result_update.ok = True
        mock_azure.sdk.requests.patch.return_value = mock_result_update

        payload = UserCSPPayload(
            tenant_id=uuid4().hex,
            display_name="Test Testerson",
            tenant_host_name="testtenant",
            email="test@testerson.test",
            password="asdfghjkl",  # pragma: allowlist secret
        )

        result = mock_azure.create_user(payload)

        assert result.id == "id"
