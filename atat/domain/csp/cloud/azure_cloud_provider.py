import json
from functools import wraps
from secrets import token_hex, token_urlsafe
from uuid import uuid4

from flask import current_app as app

from atat.utils import sha256_hex

from .cloud_provider_interface import CloudProviderInterface
from .exceptions import (
    AuthenticationException,
    ConnectionException,
    DomainNameException,
    UnknownServerException,
    UserProvisioningException,
)
from .models import (
    AdminRoleDefinitionCSPPayload,
    AdminRoleDefinitionCSPResult,
    ApplicationCSPPayload,
    ApplicationCSPResult,
    BillingInstructionCSPPayload,
    BillingInstructionCSPResult,
    BillingOwnerCSPPayload,
    BillingOwnerCSPResult,
    BillingProfileCreationCSPPayload,
    BillingProfileCreationCSPResult,
    BillingProfileTenantAccessCSPPayload,
    BillingProfileTenantAccessCSPResult,
    BillingProfileVerificationCSPPayload,
    BillingProfileVerificationCSPResult,
    CostManagementQueryCSPPayload,
    CostManagementQueryCSPResult,
    EnvironmentCSPPayload,
    EnvironmentCSPResult,
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
    TenantAdminCredentialResetCSPResult,
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
    UserCSPResult,
    UserRoleCSPPayload,
    UserRoleCSPResult,
)
from .policy import AzurePolicyManager

# This needs to be a fully pathed role definition identifier, not just a UUID
# TODO: Extract these from sdk msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD
AZURE_SKU_ID = "0001"  # probably a static sku specific to ATAT/JEDI
REMOTE_ROOT_ROLE_DEF_ID = "/providers/Microsoft.Authorization/roleDefinitions/00000000-0000-4000-8000-000000000000"

DEFAULT_POLICY_SET_DEFINITION_NAME = "Default JEDI Policy Set"


def log_and_raise_exceptions(func):
    """Wraps Azure cloud provider API calls to catch `requests` exceptions,
    log them, and re-raise them as our CSP exceptions. 

    The cloud parameter below represents an AzureCloudProvider class instance,
    i.e. `self`, since this decorator is applied to class methods.
    """

    @wraps(func)
    def wrapped_func(cloud, *args, **kwargs):
        try:
            return func(cloud, *args, **kwargs)

        except cloud.sdk.requests.exceptions.ConnectionError:
            message = f"Connection Error calling {func.__name__}"
            app.logger.error(message, exc_info=1)
            raise ConnectionException(message)

        except cloud.sdk.requests.exceptions.Timeout:
            message = f"Timeout Error calling {func.__name__}"
            app.logger.error(message, exc_info=1)
            raise ConnectionException(message)

        except cloud.sdk.requests.exceptions.HTTPError as exc:
            status_code = str(exc)[:3]
            message = f"Error calling {func.__name__}"
            app.logger.error(status_code, message, exc_info=1)
            raise UnknownServerException(status_code, f"{message}. {str(exc)}")

        except cloud.sdk.adal.AdalError as exc:
            message = f"ADAL error calling {func.__name__}"
            app.logger.error(message, exc_info=1)
            raise AuthenticationException(message)

    return wrapped_func


class AzureSDKProvider(object):
    def __init__(self):
        from azure.mgmt import managementgroups
        import azure.common.credentials as credentials
        import azure.identity as identity
        from azure.core import exceptions
        from msrestazure.azure_cloud import (
            AZURE_PUBLIC_CLOUD,
        )  # TODO: choose cloud type from config
        import adal
        import requests

        self.managementgroups = managementgroups
        self.credentials = credentials
        self.identity = identity
        self.azure_exceptions = exceptions
        self.cloud = AZURE_PUBLIC_CLOUD
        self.adal = adal
        self.requests = requests


class AzureCloudProvider(CloudProviderInterface):
    def __init__(self, config, azure_sdk_provider=None):
        self.config = config

        self.client_id = config["AZURE_CLIENT_ID"]
        self.secret_key = config["AZURE_SECRET_KEY"]
        self.tenant_id = config["AZURE_TENANT_ID"]
        self.vault_url = config["AZURE_VAULT_URL"]
        self.ps_client_id = config["AZURE_POWERSHELL_CLIENT_ID"]
        self.graph_resource = config["AZURE_GRAPH_RESOURCE"]
        self.default_aadp_qty = config["AZURE_AADP_QTY"]
        self.roles = {
            "owner": config["AZURE_ROLE_DEF_ID_OWNER"],
            "contributor": config["AZURE_ROLE_DEF_ID_CONTRIBUTOR"],
            "billing": config["AZURE_ROLE_DEF_ID_BILLING_READER"],
        }
        self.tenant_principal_app_display_name = "ATAT Remote Admin"

        if azure_sdk_provider is None:
            self.sdk = AzureSDKProvider()
        else:
            self.sdk = azure_sdk_provider

        self.policy_manager = AzurePolicyManager(config["AZURE_POLICY_LOCATION"])

    @log_and_raise_exceptions
    def _get_keyvault_token(self):
        url = (
            f"{self.sdk.cloud.endpoints.active_directory}/{self.tenant_id}/oauth2/token"
        )
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.secret_key,
            "resource": f"https://{self.sdk.cloud.suffixes.keyvault_dns[1:]}",
        }
        token_response = self.sdk.requests.get(url, data=payload, timeout=30)
        token_response.raise_for_status()
        token = token_response.json().get("access_token")
        if token is None:
            message = (
                f"Failed to get token for resource '{resource}' in tenant '{tenant_id}'"
            )
            app.logger.error(message, exc_info=1)
            raise AuthenticationException(message)
        else:
            return token

    @log_and_raise_exceptions
    def set_secret(self, secret_key, secret_value):
        kv_token = self._get_keyvault_token()

        set_secret_headers = {
            "Authorization": f"Bearer {kv_token}",
        }
        set_secret_body = {"value": secret_value}

        result = self.sdk.requests.put(
            f"{self.vault_url}secrets/{secret_key}?api-version=7.0",
            headers=set_secret_headers,
            timeout=30,
            json=set_secret_body,
        )

        result.raise_for_status()
        result_value = result.json()
        return result_value

    @log_and_raise_exceptions
    def get_secret(self, secret_key):
        kv_token = self._get_keyvault_token()

        get_secret_headers = {
            "Authorization": f"Bearer {kv_token}",
        }

        result = self.sdk.requests.get(
            f"{self.vault_url}secrets/{secret_key}?api-version=7.0",
            headers=get_secret_headers,
            timeout=30,
        )

        result.raise_for_status()
        result_value = result.json()["value"]
        return result_value

    def create_environment(self, payload: EnvironmentCSPPayload):
        creds = self._source_tenant_creds(payload.tenant_id)
        credentials = self._get_credential_obj(
            {
                "client_id": creds.tenant_sp_client_id,
                "secret_key": creds.tenant_sp_key,
                "tenant_id": creds.tenant_id,
            },
            resource=self.sdk.cloud.endpoints.resource_manager,
        )

        response = self._create_management_group(
            credentials,
            payload.management_group_name,
            payload.display_name,
            payload.parent_id,
        )

        return EnvironmentCSPResult(**response)

    @log_and_raise_exceptions
    def create_application(self, payload: ApplicationCSPPayload):
        creds = self._source_tenant_creds(payload.tenant_id)
        credentials = self._get_credential_obj(
            {
                "client_id": creds.tenant_sp_client_id,
                "secret_key": creds.tenant_sp_key,
                "tenant_id": creds.tenant_id,
            },
            resource=self.sdk.cloud.endpoints.resource_manager,
        )

        response = self._create_management_group(
            credentials,
            payload.management_group_name,
            payload.display_name,
            payload.parent_id,
        )

        return ApplicationCSPResult(**response)

    def create_initial_mgmt_group(self, payload: InitialMgmtGroupCSPPayload):
        """Creates the root management group for the Portfolio tenant.

        The management group created in this step is the parent to all future
        management groups created for applications and environments.

        A management group is a collection of subscriptions and management
        groups to which "governance conditions" can be applied. These resources
        can be nested.

        https://docs.microsoft.com/en-us/azure/governance/management-groups/overview
        """

        creds = self._source_tenant_creds(payload.tenant_id)
        credentials = self._get_credential_obj(
            {
                "client_id": creds.root_sp_client_id,
                "secret_key": creds.root_sp_key,
                "tenant_id": creds.root_tenant_id,
            },
            resource=self.sdk.cloud.endpoints.resource_manager,
        )
        response = self._create_management_group(
            credentials, payload.management_group_name, payload.display_name,
        )

        return InitialMgmtGroupCSPResult(**response)

    @log_and_raise_exceptions
    def create_initial_mgmt_group_verification(
        self, payload: InitialMgmtGroupVerificationCSPPayload
    ) -> InitialMgmtGroupVerificationCSPResult:
        """Verify the creation of the root management group.

        A management group is a collection of subscriptions and management
        groups to which "governance conditions" can be applied. These resources
        can be nested.

        https://docs.microsoft.com/en-us/azure/governance/management-groups/overview
        """
        sp_token = self._get_tenant_principal_token(self.tenant_id)
        headers = {
            "Authorization": f"Bearer {sp_token}",
        }
        response = self.sdk.requests.get(
            f"{self.sdk.cloud.endpoints.resource_manager}providers/Microsoft.Management/managementGroups/{payload.management_group_name}?api-version=2020-02-01",
            headers=headers,
        )
        response.raise_for_status()
        return InitialMgmtGroupVerificationCSPResult(**response.json())

    def _create_management_group(
        self, credentials, management_group_id, display_name, parent_id=None,
    ):
        mgmgt_group_client = self.sdk.managementgroups.ManagementGroupsAPI(credentials)
        create_parent_grp_info = self.sdk.managementgroups.models.CreateParentGroupInfo(
            id=parent_id
        )
        create_mgmt_grp_details = self.sdk.managementgroups.models.CreateManagementGroupDetails(
            parent=create_parent_grp_info
        )
        mgmt_grp_create = self.sdk.managementgroups.models.CreateManagementGroupRequest(
            name=management_group_id,
            display_name=display_name,
            details=create_mgmt_grp_details,
        )

        create_request = mgmgt_group_client.management_groups.create_or_update(
            management_group_id, mgmt_grp_create
        )

        # result is a synchronous wait, might need to do a poll instead to handle first mgmt group create
        # since we were told it could take 10+ minutes to complete, unless this handles that polling internally
        # TODO: what to do is status is not 'Succeeded' on the
        # response object? Will it always raise its own error
        # instead?
        return create_request.result()

    @log_and_raise_exceptions
    def _create_policy_definition(self, session, root_management_group_name, policy):
        create_policy_definition_uri = f"{self.sdk.cloud.endpoints.resource_manager}providers/Microsoft.Management/managementGroups/{root_management_group_name}/providers/Microsoft.Authorization/policyDefinitions/{policy.definition['properties']['displayName']}?api-version=2019-09-01"
        body = policy.definition

        result = session.put(create_policy_definition_uri, json=body, timeout=30,)
        result.raise_for_status()
        if result.status_code == 201:
            return result.json()

    @log_and_raise_exceptions
    def _create_policy_set(
        self,
        session,
        root_management_group_name,
        policy_set_definition_name,
        definition_references,
    ):
        create_policy_set_uri = f"{self.sdk.cloud.endpoints.resource_manager}providers/Microsoft.Management/managementGroups/{root_management_group_name}/providers/Microsoft.Authorization/policySetDefinitions/{policy_set_definition_name}?api-version=2019-09-01"
        body = {
            "properties": {
                "displayName": policy_set_definition_name,
                "policyDefinitions": definition_references,
                "policyType": "Custom",
            }
        }

        result = session.put(create_policy_set_uri, json=body, timeout=30,)
        result.raise_for_status()
        if result.status_code in [200, 201]:
            return result.json()

    @log_and_raise_exceptions
    def _create_policy_set_assignment(
        self, session, root_management_group_name, policy_set_definition
    ):
        create_policy_assignment_uri = f"{self.sdk.cloud.endpoints.resource_manager}providers/Microsoft.Management/managementGroups/{root_management_group_name}/providers/Microsoft.Authorization/policyAssignments/{policy_set_definition['properties']['displayName']}?api-version=2019-09-01"
        body = {
            "properties": {
                "displayName": policy_set_definition["properties"]["displayName"],
                "policyDefinitionId": policy_set_definition["id"],
            }
        }

        result = session.put(create_policy_assignment_uri, json=body, timeout=30,)
        result.raise_for_status()
        if result.status_code == 201:
            return result.json()

    def create_policies(self, payload: PoliciesCSPPayload):
        """
        Creates and applies the default JEDI Policy Set to a portfolio's root management group.

        The underlying API calls seem to be idempotent, despite the fact that most of them repeatedly
        return 201. The _create_policy_set API call is the one exception. It returns 201 on initial
        creation, and then 200 thereafter
        """

        sp_token = self._get_tenant_principal_token(payload.tenant_id)
        headers = {
            "Authorization": f"Bearer {sp_token}",
        }
        policy_session = self.sdk.requests.Session()
        policy_session.headers.update(headers)
        definition_references = []
        for policy in self.policy_manager.portfolio_definitions:
            definition = self._create_policy_definition(
                policy_session, payload.root_management_group_name, policy,
            )
            definition_references.append(
                {
                    "policyDefinitionId": definition["id"],
                    "policyDefinitionReferenceId": definition["properties"][
                        "displayName"
                    ],
                    "parameters": policy.parameters,
                }
            )
        policy_set_definition = self._create_policy_set(
            policy_session,
            payload.root_management_group_name,
            DEFAULT_POLICY_SET_DEFINITION_NAME,
            definition_references,
        )
        assign_policy_set = self._create_policy_set_assignment(
            policy_session, payload.root_management_group_name, policy_set_definition
        )
        return PoliciesCSPResult(**assign_policy_set)

    @log_and_raise_exceptions
    def disable_user(self, tenant_id, role_assignment_cloud_id):
        sp_token = self._get_tenant_principal_token(tenant_id)
        headers = {
            "Authorization": f"Bearer {sp_token}",
        }

        result = self.sdk.requests.delete(
            f"{self.sdk.cloud.endpoints.resource_manager}{role_assignment_cloud_id}?api-version=2015-07-01",
            headers=headers,
            timeout=30,
        )
        result.raise_for_status()
        return result.json()

    @log_and_raise_exceptions
    def validate_domain_name(self, name):
        response = self.sdk.requests.get(
            f"{self.sdk.cloud.endpoints.active_directory}/{name}.onmicrosoft.com/.well-known/openid-configuration",
            timeout=30,
        )
        response.raise_for_status()
        # If an existing tenant with name cannot be found, 'error' will be in the response
        return "error" in response.json()

    def generate_valid_domain_name(self, name, suffix="", max_tries=6):
        if max_tries > 0:
            domain_name = name + suffix
            if self.validate_domain_name(domain_name):
                return domain_name
            else:
                suffix = token_hex(3)
                return self.generate_valid_domain_name(name, suffix, max_tries - 1)
        else:
            raise DomainNameException(name)

    @log_and_raise_exceptions
    def create_tenant(self, payload: TenantCSPPayload):
        sp_token = self._get_root_provisioning_token()

        payload.password = token_urlsafe(16)
        payload.domain_name = self.generate_valid_domain_name(payload.domain_name)
        create_tenant_body = payload.dict(by_alias=True)

        create_tenant_headers = {
            "Authorization": f"Bearer {sp_token}",
        }

        result = self.sdk.requests.post(
            f"{self.sdk.cloud.endpoints.resource_manager}providers/Microsoft.SignUp/createTenant?api-version=2020-01-01-preview",
            json=create_tenant_body,
            headers=create_tenant_headers,
            timeout=30,
        )
        result.raise_for_status()

        result_dict = result.json()
        tenant_id = result_dict.get("tenantId")
        tenant_admin_username = f"{payload.user_id}@{payload.domain_name}.{self.config.get('OFFICE_365_DOMAIN')}"

        self.create_tenant_creds(
            tenant_id,
            KeyVaultCredentials(
                root_tenant_id=self.tenant_id,
                root_sp_client_id=self.client_id,
                root_sp_key=self.secret_key,
                tenant_id=tenant_id,
                tenant_admin_username=tenant_admin_username,
                tenant_admin_password=payload.password,
            ),
        )

        return TenantCSPResult(domain_name=payload.domain_name, **result_dict)

    @log_and_raise_exceptions
    def create_billing_profile_creation(
        self, payload: BillingProfileCreationCSPPayload
    ):
        """Create a billing profile which specifies which products are included
            in an invoice, and how the invoice is paid for.

            Billing profiles include:
            - Payment methods
            - Contact info
            - Permissions

            https://docs.microsoft.com/en-us/microsoft-store/billing-profile
            """
        sp_token = self._get_root_provisioning_token()

        create_billing_account_body = payload.dict(by_alias=True)

        create_billing_account_headers = {
            "Authorization": f"Bearer {sp_token}",
        }

        billing_account_create_url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Billing/billingAccounts/{payload.billing_account_name}/billingProfiles?api-version=2019-10-01-preview"

        result = self.sdk.requests.post(
            billing_account_create_url,
            json=create_billing_account_body,
            headers=create_billing_account_headers,
            timeout=30,
        )
        result.raise_for_status()
        if result.status_code == 202:
            # 202 has location/retry after headers
            return BillingProfileCreationCSPResult(**result.headers)
        elif result.status_code == 200:
            # NB: Swagger docs imply call can sometimes resolve immediately
            return BillingProfileVerificationCSPResult(**result.json())

    @log_and_raise_exceptions
    def create_billing_profile_verification(
        self, payload: BillingProfileVerificationCSPPayload
    ):
        """Verify that a billing profile has been created.

            A billing profile specifies which products are included in an invoice,
            and how the invoice is paid for. They include:
            - Payment methods
            - Contact info
            - Permissions

            https://docs.microsoft.com/en-us/microsoft-store/billing-profile
            """
        sp_token = self._get_root_provisioning_token()

        auth_header = {
            "Authorization": f"Bearer {sp_token}",
        }

        result = self.sdk.requests.get(
            payload.billing_profile_verify_url, headers=auth_header, timeout=30,
        )
        result.raise_for_status()

        if result.status_code == 202:
            # 202 has location/retry after headers
            return BillingProfileCreationCSPResult(**result.headers)
        elif result.status_code == 200:
            return BillingProfileVerificationCSPResult(**result.json())

    @log_and_raise_exceptions
    def create_billing_profile_tenant_access(
        self, payload: BillingProfileTenantAccessCSPPayload
    ):
        sp_token = self._get_root_provisioning_token()
        request_body = {
            "properties": {
                "principalTenantId": payload.tenant_id,  # from tenant creation
                "principalId": payload.user_object_id,  # from tenant creation
                "roleDefinitionId": f"/providers/Microsoft.Billing/billingAccounts/{payload.billing_account_name}/billingProfiles/{payload.billing_profile_name}/billingRoleDefinitions/40000000-aaaa-bbbb-cccc-100000000000",
            }
        }

        headers = {
            "Authorization": f"Bearer {sp_token}",
        }

        url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Billing/billingAccounts/{payload.billing_account_name}/billingProfiles/{payload.billing_profile_name}/createBillingRoleAssignment?api-version=2019-10-01-preview"
        result = self.sdk.requests.post(
            url, headers=headers, json=request_body, timeout=30,
        )
        result.raise_for_status()
        if result.status_code == 201:
            return BillingProfileTenantAccessCSPResult(**result.json())

    @log_and_raise_exceptions
    def create_task_order_billing_creation(
        self, payload: TaskOrderBillingCreationCSPPayload
    ):
        sp_token = self._get_root_provisioning_token()
        request_body = [
            {
                "op": "replace",
                "path": "/enabledAzurePlans",
                "value": [{"skuId": AZURE_SKU_ID}],
            }
        ]

        request_headers = {
            "Authorization": f"Bearer {sp_token}",
        }

        url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Billing/billingAccounts/{payload.billing_account_name}/billingProfiles/{payload.billing_profile_name}?api-version=2019-10-01-preview"

        result = self.sdk.requests.patch(
            url, headers=request_headers, json=request_body, timeout=30,
        )
        result.raise_for_status()

        if result.status_code == 202:
            # 202 has location/retry after headers
            return TaskOrderBillingCreationCSPResult(**result.headers)
        elif result.status_code == 200:
            return TaskOrderBillingVerificationCSPResult(**result.json())

    @log_and_raise_exceptions
    def create_task_order_billing_verification(
        self, payload: TaskOrderBillingVerificationCSPPayload
    ):
        sp_token = self._get_root_provisioning_token()

        auth_header = {
            "Authorization": f"Bearer {sp_token}",
        }

        result = self.sdk.requests.get(
            payload.task_order_billing_verify_url, headers=auth_header, timeout=30,
        )
        result.raise_for_status()

        if result.status_code == 202:
            # 202 has location/retry after headers
            return TaskOrderBillingCreationCSPResult(**result.headers)
        elif result.status_code == 200:
            return TaskOrderBillingVerificationCSPResult(**result.json())

    @log_and_raise_exceptions
    def create_billing_instruction(self, payload: BillingInstructionCSPPayload):
        sp_token = self._get_root_provisioning_token()

        request_body = {
            "properties": {
                "amount": payload.initial_clin_amount,
                "startDate": payload.initial_clin_start_date,
                "endDate": payload.initial_clin_end_date,
            }
        }

        url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Billing/billingAccounts/{payload.billing_account_name}/billingProfiles/{payload.billing_profile_name}/instructions/{payload.initial_task_order_id}:CLIN00{payload.initial_clin_type}?api-version=2019-10-01-preview"

        auth_header = {
            "Authorization": f"Bearer {sp_token}",
        }

        result = self.sdk.requests.put(
            url, headers=auth_header, json=request_body, timeout=30
        )
        result.raise_for_status()
        return BillingInstructionCSPResult(**result.json())

    @log_and_raise_exceptions
    def create_subscription(self, payload: SubscriptionCreationCSPPayload):
        sp_token = self._get_tenant_principal_token(payload.tenant_id)

        request_body = {
            "displayName": payload.display_name,
            "skuId": AZURE_SKU_ID,
            "managementGroupId": payload.parent_group_id,
        }

        url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Billing/billingAccounts/{payload.billing_account_name}/billingProfiles/{payload.billing_profile_name}/invoiceSections/{payload.invoice_section_name}/providers/Microsoft.Subscription/createSubscription?api-version=2019-10-01-preview"

        auth_header = {
            "Authorization": f"Bearer {sp_token}",
        }

        result = self.sdk.requests.put(
            url, headers=auth_header, json=request_body, timeout=30
        )
        result.raise_for_status()
        if result.status_code in [200, 202]:
            # 202 has location/retry after headers
            return SubscriptionCreationCSPResult(**result.headers, **result.json())

    def create_subscription_creation(self, payload: SubscriptionCreationCSPPayload):
        return self.create_subscription(payload)

    @log_and_raise_exceptions
    def create_subscription_verification(
        self, payload: SubscriptionVerificationCSPPayload
    ):
        sp_token = self._get_tenant_principal_token(payload.tenant_id)

        auth_header = {
            "Authorization": f"Bearer {sp_token}",
        }

        result = self.sdk.requests.get(
            payload.subscription_verify_url, headers=auth_header, timeout=30
        )
        result.raise_for_status()

        # 202 has location/retry after headers
        return SuscriptionVerificationCSPResult(**result.json())

    @log_and_raise_exceptions
    def create_product_purchase(self, payload: ProductPurchaseCSPPayload):
        sp_token = self._get_root_provisioning_token()

        create_product_purchase_body = {
            "type": "AADPremium",
            "sku": "AADP1",
            "productProperties": {"beneficiaryTenantId": payload.tenant_id,},
            "quantity": self.default_aadp_qty,
        }
        create_product_purchase_headers = {
            "Authorization": f"Bearer {sp_token}",
        }

        product_purchase_url = f"https://management.azure.com/providers/Microsoft.Billing/billingAccounts/{payload.billing_account_name}/billingProfiles/{payload.billing_profile_name}/purchaseProduct?api-version=2019-10-01-preview"

        result = self.sdk.requests.post(
            product_purchase_url,
            json=create_product_purchase_body,
            headers=create_product_purchase_headers,
            timeout=30,
        )
        result.raise_for_status()

        if result.status_code == 202:
            # 202 has location/retry after headers
            return ProductPurchaseCSPResult(**result.headers)
        elif result.status_code == 200:
            # NB: Swagger docs imply call can sometimes resolve immediately
            return ProductPurchaseVerificationCSPResult(**result.json())

    @log_and_raise_exceptions
    def create_product_purchase_verification(
        self, payload: ProductPurchaseVerificationCSPPayload
    ):
        sp_token = self._get_root_provisioning_token()

        auth_header = {
            "Authorization": f"Bearer {sp_token}",
        }

        result = self.sdk.requests.get(
            payload.product_purchase_verify_url, headers=auth_header, timeout=30
        )
        result.raise_for_status()

        if result.status_code == 202:
            # 202 has location/retry after headers
            return ProductPurchaseCSPResult(**result.headers)
        elif result.status_code == 200:
            premium_purchase_date = result.json()["properties"]["purchaseDate"]
            return ProductPurchaseVerificationCSPResult(
                premium_purchase_date=premium_purchase_date
            )

    def create_tenant_admin_credential_reset(
        self, payload: TenantAdminCredentialResetCSPPayload
    ):
        """Reset tenant admin password to random value.

        The purpose of this call is to set the password for the tenant admin
        user to a value that is not stored anywhere. You're essentially making
        ATAT "forget" the human admin's login creds when it's done with them.
        """

        graph_token = self._get_tenant_admin_token(
            payload.tenant_id, self.graph_resource
        )
        self._update_active_directory_user_password_profile(graph_token, payload)

        return TenantAdminCredentialResetCSPResult()

    @log_and_raise_exceptions
    def create_tenant_admin_ownership(self, payload: TenantAdminOwnershipCSPPayload):
        """Gives the tenant admin (human user) the Owner role on the root management group."""

        mgmt_token = self._get_elevated_management_token(payload.tenant_id)

        role_definition_id = f"/providers/Microsoft.Management/managementGroups/{payload.tenant_id}/providers/Microsoft.Authorization/roleDefinitions/{self.roles['owner']}"

        request_body = {
            "properties": {
                "roleDefinitionId": role_definition_id,
                "principalId": payload.user_object_id,
            }
        }

        auth_header = {
            "Authorization": f"Bearer {mgmt_token}",
        }

        assignment_guid = str(uuid4())

        url = f"{self.sdk.cloud.endpoints.resource_manager}providers/Microsoft.Management/managementGroups/{payload.tenant_id}/providers/Microsoft.Authorization/roleAssignments/{assignment_guid}?api-version=2015-07-01"

        result = self.sdk.requests.put(
            url, headers=auth_header, json=request_body, timeout=30
        )
        result.raise_for_status()

        return TenantAdminOwnershipCSPResult(**result.json())

    @log_and_raise_exceptions
    def create_tenant_principal_ownership(
        self, payload: TenantPrincipalOwnershipCSPPayload
    ):
        """Gives the service principal the owner role over the root management group.

        The security principal object defines the access policy and permissions
        for the user/application in the Azure AD tenant.

        https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals
        """

        mgmt_token = self._get_elevated_management_token(payload.tenant_id)

        # NOTE: the tenant_id is also the id of the root management group, once it is created
        role_definition_id = f"/providers/Microsoft.Management/managementGroups/{payload.tenant_id}/providers/Microsoft.Authorization/roleDefinitions/{self.roles['owner']}"

        request_body = {
            "properties": {
                "roleDefinitionId": role_definition_id,
                "principalId": payload.principal_id,
            }
        }

        auth_header = {
            "Authorization": f"Bearer {mgmt_token}",
        }

        assignment_guid = str(uuid4())

        url = f"{self.sdk.cloud.endpoints.resource_manager}providers/Microsoft.Management/managementGroups/{payload.tenant_id}/providers/Microsoft.Authorization/roleAssignments/{assignment_guid}?api-version=2015-07-01"

        result = self.sdk.requests.put(
            url, headers=auth_header, json=request_body, timeout=30,
        )
        result.raise_for_status()
        return TenantPrincipalOwnershipCSPResult(**result.json())

    @log_and_raise_exceptions
    def create_tenant_principal_app(self, payload: TenantPrincipalAppCSPPayload):
        """Creates an app registration for a Profile.

        An Azure AD application is defined by its one and only application
        object, which resides in the Azure AD tenant where the application was
        registered, known as the application's "home" tenant.

        https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals
        https://docs.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0
        """

        graph_token = self._get_tenant_admin_token(
            payload.tenant_id, self.graph_resource
        )
        request_body = {"displayName": self.tenant_principal_app_display_name}

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/v1.0/applications"

        result = self.sdk.requests.post(
            url, json=request_body, headers=auth_header, timeout=30
        )
        result.raise_for_status()
        return TenantPrincipalAppCSPResult(**result.json())

    @log_and_raise_exceptions
    def create_tenant_principal(self, payload: TenantPrincipalCSPPayload):
        """Creates a service principal for a Profile.
        A service principal represents an instance of an application in a
        directory.

        https://docs.microsoft.com/en-us/graph/api/resources/serviceprincipal?view=graph-rest-beta
        https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals
        """
        graph_token = self._get_tenant_admin_token(
            payload.tenant_id, self.graph_resource
        )
        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }
        request_body = {"appId": payload.principal_app_id}

        url = f"{self.graph_resource}/beta/servicePrincipals"

        result = self.sdk.requests.post(
            url, json=request_body, headers=auth_header, timeout=30
        )
        result.raise_for_status()
        return TenantPrincipalCSPResult(**result.json())

    @log_and_raise_exceptions
    def create_tenant_principal_credential(
        self, payload: TenantPrincipalCredentialCSPPayload
    ):
        graph_token = self._get_tenant_admin_token(
            payload.tenant_id, self.graph_resource
        )
        request_body = {
            "passwordCredentials": [{"displayName": "ATAT Generated Password"}]
        }

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/v1.0/applications/{payload.principal_app_object_id}/addPassword"

        result = self.sdk.requests.post(
            url, json=request_body, headers=auth_header, timeout=30
        )
        result.raise_for_status()
        result_json = result.json()
        self.update_tenant_creds(
            payload.tenant_id,
            KeyVaultCredentials(
                tenant_id=payload.tenant_id,
                tenant_sp_key=result_json.get("secretText"),
                tenant_sp_client_id=payload.principal_app_id,
            ),
        )
        return TenantPrincipalCredentialCSPResult(
            principal_client_id=payload.principal_app_id,
            principal_creds_established=True,
        )

    @log_and_raise_exceptions
    def create_admin_role_definition(self, payload: AdminRoleDefinitionCSPPayload):
        """Fetch the UUID for the "Global Admin" / "Company Admin" role."""

        graph_token = self._get_tenant_admin_token(
            payload.tenant_id, self.graph_resource
        )
        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/beta/roleManagement/directory/roleDefinitions"

        response = self.sdk.requests.get(url, headers=auth_header, timeout=30)
        response.raise_for_status()

        result = response.json()
        roleList = result.get("value")

        DEFAULT_ADMIN_RD_ID = "794bb258-3e31-42ff-9ee4-731a72f62851"
        admin_role_def_id = next(
            (
                role.get("id")
                for role in roleList
                if role.get("displayName") == "Company Administrator"
            ),
            DEFAULT_ADMIN_RD_ID,
        )

        return AdminRoleDefinitionCSPResult(admin_role_def_id=admin_role_def_id)

    @log_and_raise_exceptions
    def create_principal_admin_role(self, payload: PrincipalAdminRoleCSPPayload):
        """Grant the "Global Admin" / "Company Admin" role to the service
        principal (create a role assignment).
        """

        graph_token = self._get_tenant_admin_token(
            payload.tenant_id, self.graph_resource
        )
        request_body = {
            "principalId": payload.principal_id,
            "roleDefinitionId": payload.admin_role_def_id,
            "resourceScope": "/",
        }

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/beta/roleManagement/directory/roleAssignments"

        result = self.sdk.requests.post(
            url, headers=auth_header, json=request_body, timeout=30
        )
        result.raise_for_status()
        return PrincipalAdminRoleCSPResult(**result.json())

    def create_billing_owner(self, payload: BillingOwnerCSPPayload):
        """Create a billing account owner, which is a billing role that can
        manage everything for a billing account.

        https://docs.microsoft.com/en-us/azure/cost-management-billing/manage/understand-mca-roles
        """

        graph_token = self._get_tenant_principal_token(
            payload.tenant_id, resource=self.graph_resource
        )

        # Step 1: Create an AAD identity for the user
        user_result = self._create_active_directory_user(graph_token, payload)
        # Step 2: Set the recovery email
        self._update_active_directory_user_email(graph_token, user_result.id, payload)
        # Step 3: Find the Billing Administrator role ID
        billing_admin_role_id = self._get_billing_owner_role(graph_token)
        # Step 4: Assign the Billing Administrator role to the new user
        self._assign_billing_owner_role(
            graph_token, billing_admin_role_id, user_result.id
        )

        return BillingOwnerCSPResult(billing_owner_id=user_result.id)

    @log_and_raise_exceptions
    def _assign_billing_owner_role(self, graph_token, billing_admin_role_id, user_id):
        request_body = {
            "roleDefinitionId": billing_admin_role_id,
            "principalId": user_id,
            "resourceScope": "/",
        }

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/beta/roleManagement/directory/roleAssignments"

        result = self.sdk.requests.post(url, headers=auth_header, json=request_body)
        result.raise_for_status()

        if result.ok:
            return True
        else:
            raise UserProvisioningException("Could not assign billing admin role")

    @log_and_raise_exceptions
    def _get_billing_owner_role(self, graph_token):
        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/v1.0/directoryRoles"
        result = self.sdk.requests.get(url, headers=auth_header)
        result.raise_for_status()

        if result.ok:
            result = result.json()
            for role in result["value"]:
                if role["displayName"] == "Billing Administrator":
                    return role["id"]
        else:
            raise UserProvisioningException(
                "Could not find Billing Administrator role ID; role may not be enabled."
            )

    def create_user(self, payload: UserCSPPayload) -> UserCSPResult:
        """Create a user in an Azure Active Directory instance.
        Unlike most of the methods on this interface, this requires
        two API calls: one POST to create the user and one PATCH to
        set the alternate email address. The email address cannot
        be set on the first API call. The email address is
        necessary so that users can do Self-Service Password
        Recovery.

        Arguments:
            payload {UserCSPPayload} -- a payload object with the
            data necessary for both calls

        Returns:
            UserCSPResult -- a result object containing the AAD ID.
        """
        graph_token = self._get_tenant_principal_token(
            payload.tenant_id, resource=self.graph_resource
        )

        result = self._create_active_directory_user(graph_token, payload)
        self._update_active_directory_user_email(graph_token, result.id, payload)

        return result

    @log_and_raise_exceptions
    def _create_active_directory_user(self, graph_token, payload) -> UserCSPResult:
        request_body = {
            "accountEnabled": True,
            "displayName": payload.display_name,
            "mailNickname": payload.mail_nickname,
            "userPrincipalName": payload.user_principal_name,
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": payload.password,
            },
        }

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/v1.0/users"

        result = self.sdk.requests.post(
            url, headers=auth_header, json=request_body, timeout=30
        )
        result.raise_for_status()

        return UserCSPResult(**result.json())

    @log_and_raise_exceptions
    def _update_active_directory_user_email(self, graph_token, user_id, payload):
        request_body = {"otherMails": [payload.email]}

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/v1.0/users/{user_id}"

        result = self.sdk.requests.patch(
            url, headers=auth_header, json=request_body, timeout=30
        )
        result.raise_for_status()

        if result.ok:
            return True
        else:
            raise UserProvisioningException(
                f"Failed update user email: {response.json()}"
            )

    @log_and_raise_exceptions
    def _update_active_directory_user_password_profile(self, graph_token, payload):
        request_body = {
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "forceChangePasswordNextSignInWithMfa": False,
                "password": payload.new_password or token_urlsafe(16),
            }
        }

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/v1.0/users/{payload.user_object_id}"

        result = self.sdk.requests.patch(
            url, headers=auth_header, json=request_body, timeout=30
        )
        result.raise_for_status()

        if result.ok:
            return True
        else:
            raise UserProvisioningException(
                f"Failed update user password profile: {response.json()}"
            )

    def create_user_role(self, payload: UserRoleCSPPayload):
        graph_token = self._get_tenant_principal_token(payload.tenant_id)

        role_guid = self.roles[payload.role]
        role_definition_id = f"{payload.management_group_id}/providers/Microsoft.Authorization/roleDefinitions/{role_guid}"

        request_body = {
            "properties": {
                "roleDefinitionId": role_definition_id,
                "principalId": payload.user_object_id,
            }
        }

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        assignment_guid = str(uuid4())

        url = f"{self.sdk.cloud.endpoints.resource_manager}{payload.management_group_id}/providers/Microsoft.Authorization/roleAssignments/{assignment_guid}?api-version=2015-07-01"

        response = self.sdk.requests.put(url, headers=auth_header, json=request_body)

        if response.ok:
            return UserRoleCSPResult(**response.json())
        else:
            raise UserProvisioningException(
                f"Failed to create user role assignment: {response.json()}"
            )

    def _extract_subscription_id(self, subscription_url):
        sub_id_match = SUBSCRIPTION_ID_REGEX.match(subscription_url)

        if sub_id_match:
            return sub_id_match.group(1)

    def _get_tenant_admin_token(self, tenant_id, resource):
        creds = self._source_tenant_creds(tenant_id)
        return self._get_user_principal_token_for_resource(
            creds.tenant_admin_username,
            creds.tenant_admin_password,
            creds.tenant_id,
            resource,
        )

    def _get_root_provisioning_token(self):
        creds = self._source_root_creds()
        return self._get_service_principal_token(
            creds.root_tenant_id, creds.root_sp_client_id, creds.root_sp_key
        )

    @log_and_raise_exceptions
    def _get_service_principal_token(
        self, tenant_id, client_id, secret_key, resource=None
    ):
        context = self.sdk.adal.AuthenticationContext(
            f"{self.sdk.cloud.endpoints.active_directory}/{tenant_id}"
        )
        resource = resource or self.sdk.cloud.endpoints.resource_manager
        token_response = context.acquire_token_with_client_credentials(
            resource, client_id, secret_key
        )

        token = token_response.get("accessToken")
        if token is None:
            message = f"Failed to get service principal token for resource '{resource}' in tenant '{tenant_id}'"
            app.logger.error(message, exc_info=1)
            raise AuthenticationException(message)
        else:
            return token

    @log_and_raise_exceptions
    def _get_user_principal_token_for_resource(
        self, username, password, tenant_id, resource
    ):
        context = self.sdk.adal.AuthenticationContext(
            f"{self.sdk.cloud.endpoints.active_directory}/{tenant_id}"
        )
        token_response = context.acquire_token_with_username_password(
            resource, username, password, self.ps_client_id
        )

        token = token_response.get("accessToken")
        if token is None:
            message = f"Failed to get service principal token for resource '{resource}' in tenant '{tenant_id}'"
            app.logger.error(message, exc_info=1)
            raise AuthenticationException(message)
        else:
            return token

    def _get_credential_obj(self, creds, resource=None):
        return self.sdk.credentials.ServicePrincipalCredentials(
            client_id=creds.get("client_id"),
            secret=creds.get("secret_key"),
            tenant=creds.get("tenant_id"),
            resource=resource,
            cloud_environment=self.sdk.cloud,
        )

    def _get_client_secret_credential_obj(self):
        creds = self._source_root_creds()
        return self.sdk.identity.ClientSecretCredential(
            tenant_id=creds.root_tenant_id,
            client_id=creds.root_sp_client_id,
            client_secret=creds.root_sp_key,
        )

    @property
    def _root_creds(self):
        return {
            "client_id": self.client_id,
            "secret_key": self.secret_key,
            "tenant_id": self.tenant_id,
        }

    def _get_tenant_principal_token(self, tenant_id, resource=None):
        creds = self._source_tenant_creds(tenant_id)
        return self._get_service_principal_token(
            creds.tenant_id,
            creds.tenant_sp_client_id,
            creds.tenant_sp_key,
            resource=resource,
        )

    @log_and_raise_exceptions
    def _get_elevated_management_token(self, tenant_id):
        mgmt_token = self._get_tenant_admin_token(
            tenant_id, self.sdk.cloud.endpoints.resource_manager
        )

        auth_header = {
            "Authorization": f"Bearer {mgmt_token}",
        }
        url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Authorization/elevateAccess?api-version=2016-07-01"

        result = self.sdk.requests.post(url, headers=auth_header, timeout=30)
        result.raise_for_status()
        if not result.ok:
            raise AuthenticationException("Failed to elevate access")

        return mgmt_token

    def _source_root_creds(self):
        return KeyVaultCredentials(
            root_tenant_id=self._root_creds.get("tenant_id"),
            root_sp_client_id=self._root_creds.get("client_id"),
            root_sp_key=self._root_creds.get("secret_key"),
        )

    def create_tenant_creds(
        self, tenant_id, secret: KeyVaultCredentials
    ) -> KeyVaultCredentials:
        hashed = sha256_hex(tenant_id)
        self.set_secret(hashed, json.dumps(secret.dict()))
        return secret

    def update_tenant_creds(
        self, tenant_id, secret: KeyVaultCredentials
    ) -> KeyVaultCredentials:
        hashed = sha256_hex(tenant_id)
        curr_secrets = self._source_tenant_creds(tenant_id)
        updated_secrets = curr_secrets.merge_credentials(secret)
        self.set_secret(hashed, json.dumps(updated_secrets.dict()))
        return updated_secrets

    def _source_tenant_creds(self, tenant_id) -> KeyVaultCredentials:
        hashed = sha256_hex(tenant_id)
        raw_creds = self.get_secret(hashed)
        return KeyVaultCredentials(**json.loads(raw_creds))

    @log_and_raise_exceptions
    def get_reporting_data(self, payload: CostManagementQueryCSPPayload):
        """
        Queries the Cost Management API for an invoice section's raw reporting data

        We query at the invoiceSection scope. The full scope path is passed in
        with the payload at the `invoice_section_id` key.
        """
        token = self._get_tenant_principal_token(payload.tenant_id)

        headers = {"Authorization": f"Bearer {token}"}

        request_body = {
            "type": "Usage",
            "timeframe": "Custom",
            "timePeriod": {"from": payload.from_date, "to": payload.to_date,},
            "dataset": {
                "granularity": "Monthly",
                "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}},
                "grouping": [{"type": "Dimension", "name": "InvoiceId"}],
            },
        }
        cost_mgmt_url = (
            f"/providers/Microsoft.CostManagement/query?api-version=2019-11-01"
        )
        result = self.sdk.requests.post(
            f"{self.sdk.cloud.endpoints.resource_manager}{payload.invoice_section_id}{cost_mgmt_url}",
            json=request_body,
            headers=headers,
            timeout=30,
        )
        result.raise_for_status()
        if result.ok:
            return CostManagementQueryCSPResult(**result.json())

    @log_and_raise_exceptions
    def _get_calculator_creds(self):
        authority = f"{self.sdk.cloud.endpoints.active_directory}/{self.tenant_id}"
        context = self.sdk.adal.AuthenticationContext(authority=authority)
        calc_resource = self.config.get("AZURE_CALC_RESOURCE")
        token_response = context.acquire_token_with_client_credentials(
            calc_resource,
            self.config.get("AZURE_CALC_CLIENT_ID"),
            self.config.get("AZURE_CALC_SECRET"),
        )
        token = token_response.get("accessToken")
        if token is None:
            message = f"Failed to get token for resource '{calc_resource}' in tenant '{tenant_id}'"
            app.logger.error(message, exc_info=1)
            raise AuthenticationException(message)
        else:
            return token

    def get_calculator_url(self):
        calc_access_token = self._get_calculator_creds()
        return f"{self.config.get('AZURE_CALC_URL')}?access_token={calc_access_token}"
