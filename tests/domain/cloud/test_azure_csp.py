import pytest
from unittest.mock import Mock

from uuid import uuid4

from atst.domain.csp.cloud import AzureCloudProvider

from tests.mock_azure import mock_azure, AUTH_CREDENTIALS
from tests.factories import EnvironmentFactory, ApplicationFactory


# TODO: Directly test create subscription, provide all args √
# TODO: Test create environment (create management group with parent)
# TODO: Test create application (create manageemnt group with parent)
# Create reusable mock for mocking the management group calls for multiple services
#


def test_create_subscription_succeeds(mock_azure: AzureCloudProvider):
    environment = EnvironmentFactory.create()

    subscription_id = str(uuid4())

    credentials = mock_azure._get_credential_obj(AUTH_CREDENTIALS)
    display_name = "Test Subscription"
    billing_profile_id = str(uuid4())
    sku_id = str(uuid4())
    management_group_id = (
        environment.cloud_id  # environment.csp_details.management_group_id?
    )
    billing_account_name = (
        "?"  # environment.application.portfilio.csp_details.billing_account.name?
    )
    invoice_section_name = "?"  # environment.name? or something specific to billing?

    mock_azure.sdk.subscription.SubscriptionClient.return_value.subscription_factory.create_subscription.return_value.result.return_value.subscription_link = (
        f"subscriptions/{subscription_id}"
    )

    result = mock_azure._create_subscription(
        credentials,
        display_name,
        billing_profile_id,
        sku_id,
        management_group_id,
        billing_account_name,
        invoice_section_name,
    )

    assert result == subscription_id


def mock_management_group_create(mock_azure, spec_dict):
    mock_azure.sdk.managementgroups.ManagementGroupsAPI.return_value.management_groups.create_or_update.return_value.result.return_value = Mock(
        **spec_dict
    )


def test_create_environment_succeeds(mock_azure: AzureCloudProvider):
    environment = EnvironmentFactory.create()

    mock_management_group_create(mock_azure, {"id": "Test Id"})

    result = mock_azure.create_environment(
        AUTH_CREDENTIALS, environment.creator, environment
    )

    assert result.id == "Test Id"


def test_create_application_succeeds(mock_azure: AzureCloudProvider):
    application = ApplicationFactory.create()

    mock_management_group_create(mock_azure, {"id": "Test Id"})

    result = mock_azure._create_application(AUTH_CREDENTIALS, application)

    assert result.id == "Test Id"


def test_create_atat_admin_user_succeeds(mock_azure: AzureCloudProvider):
    environment_id = str(uuid4())

    csp_user_id = str(uuid4)

    mock_azure.sdk.graphrbac.GraphRbacManagementClient.return_value.service_principals.create.return_value.object_id = (
        csp_user_id
    )

    result = mock_azure.create_atat_admin_user(AUTH_CREDENTIALS, environment_id)

    assert result.get("csp_user_id") == csp_user_id


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
