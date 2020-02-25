import json
from secrets import token_urlsafe
from uuid import uuid4
from flask import current_app as app

from atst.utils import sha256_hex

from .cloud_provider_interface import CloudProviderInterface
from .exceptions import (
    AuthenticationException,
    UserProvisioningException,
    ConnectionException,
    UnknownServerException,
    SecretException,
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
    CostManagementQueryCSPResult,
    InitialMgmtGroupCSPPayload,
    InitialMgmtGroupCSPResult,
    InitialMgmtGroupVerificationCSPPayload,
    InitialMgmtGroupVerificationCSPResult,
    EnvironmentCSPPayload,
    EnvironmentCSPResult,
    KeyVaultCredentials,
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
    UserCSPResult,
    UserRoleCSPPayload,
    UserRoleCSPResult,
)
from .policy import AzurePolicyManager

# This needs to be a fully pathed role definition identifier, not just a UUID
# TODO: Extract these from sdk msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD
AZURE_SKU_ID = "0001"  # probably a static sku specific to ATAT/JEDI
REMOTE_ROOT_ROLE_DEF_ID = "/providers/Microsoft.Authorization/roleDefinitions/00000000-0000-4000-8000-000000000000"


class AzureSDKProvider(object):
    def __init__(self):
        from azure.mgmt import subscription, authorization, managementgroups
        from azure.mgmt.resource import policy
        import azure.graphrbac as graphrbac
        import azure.common.credentials as credentials
        import azure.identity as identity
        from azure.keyvault import secrets
        from azure.core import exceptions
        from msrestazure.azure_cloud import (
            AZURE_PUBLIC_CLOUD,
        )  # TODO: choose cloud type from config
        import adal
        import requests

        self.subscription = subscription
        self.policy = policy
        self.managementgroups = managementgroups
        self.authorization = authorization
        self.adal = adal
        self.graphrbac = graphrbac
        self.credentials = credentials
        self.identity = identity
        self.azure_exceptions = exceptions
        self.secrets = secrets
        self.requests = requests
        self.cloud = AZURE_PUBLIC_CLOUD


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

        if azure_sdk_provider is None:
            self.sdk = AzureSDKProvider()
        else:
            self.sdk = azure_sdk_provider

        self.policy_manager = AzurePolicyManager(config["AZURE_POLICY_LOCATION"])

    def set_secret(self, secret_key, secret_value):
        credential = self._get_client_secret_credential_obj()
        secret_client = self.sdk.secrets.SecretClient(
            vault_url=self.vault_url, credential=credential,
        )
        try:
            return secret_client.set_secret(secret_key, secret_value)
        except self.sdk.azure_exceptions.HttpResponseError:
            app.logger.error(
                f"Could not SET secret in Azure keyvault for key {secret_key}.",
                exc_info=1,
            )
            creds = self._source_creds()
            raise SecretException(
                creds.tenant_id,
                f"Could not SET secret in Azure keyvault for key {secret_key}.",
            )

    def get_secret(self, secret_key):
        credential = self._get_client_secret_credential_obj()
        secret_client = self.sdk.secrets.SecretClient(
            vault_url=self.vault_url, credential=credential,
        )
        try:
            return secret_client.get_secret(secret_key).value
        except self.sdk.azure_exceptions.HttpResponseError:
            app.logger.error(
                f"Could not GET secret in Azure keyvault for key {secret_key}.",
                exc_info=1,
            )
            creds = self._source_creds()
            raise SecretException(
                creds.tenant_id,
                f"Could not GET secret in Azure keyvault for key {secret_key}.",
            )

    def create_environment(self, payload: EnvironmentCSPPayload):
        creds = self._source_creds(payload.tenant_id)
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

    def create_application(self, payload: ApplicationCSPPayload):
        creds = self._source_creds(payload.tenant_id)
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
        creds = self._source_creds(payload.tenant_id)
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

    def create_initial_mgmt_group_verification(
        self, payload: InitialMgmtGroupVerificationCSPPayload
    ):
        creds = self._source_creds(payload.tenant_id)
        credentials = self._get_credential_obj(
            {
                "client_id": creds.root_sp_client_id,
                "secret_key": creds.root_sp_key,
                "tenant_id": creds.root_tenant_id,
            },
            resource=self.sdk.cloud.endpoints.resource_manager,
        )

        response = self._get_management_group(credentials, payload.tenant_id,)
        return InitialMgmtGroupVerificationCSPResult(**response.result())

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

    def _get_management_group(self, credentials, management_group_id):
        mgmgt_group_client = self.sdk.managementgroups.ManagementGroupsAPI(credentials)
        response = mgmgt_group_client.management_groups.get(management_group_id)
        return response

    def _create_policy_definition(
        self, credentials, subscription_id, management_group_id, properties,
    ):
        """
        Requires credentials that have AZURE_MANAGEMENT_API
        specified as the resource. The Service Principal
        specified in the credentials must have the "Resource
        Policy Contributor" role assigned with a scope at least
        as high as the management group specified by
        management_group_id.

        Arguments:
            credentials -- ServicePrincipalCredentials
            subscription_id -- str, ID of the subscription (just the UUID, not the path)
            management_group_id -- str, ID of the management group (just the UUID, not the path)
            properties -- dictionary, the "properties" section of a valid Azure policy definition document

        Returns:
            azure.mgmt.resource.policy.[api version].models.PolicyDefinition: the PolicyDefinition object provided to Azure

        Raises:
            TBD
        """
        # TODO: which subscription would this be?
        client = self.sdk.policy.PolicyClient(credentials, subscription_id)

        definition = client.policy_definitions.models.PolicyDefinition(
            policy_type=properties.get("policyType"),
            mode=properties.get("mode"),
            display_name=properties.get("displayName"),
            description=properties.get("description"),
            policy_rule=properties.get("policyRule"),
            parameters=properties.get("parameters"),
        )

        name = properties.get("displayName")

        return client.policy_definitions.create_or_update_at_management_group(
            policy_definition_name=name,
            parameters=definition,
            management_group_id=management_group_id,
        )

    def disable_user(self, tenant_id, role_assignment_cloud_id):
        sp_token = self._get_tenant_principal_token(tenant_id)
        if sp_token is None:
            raise AuthenticationException("Could not resolve token in disable user")
        headers = {
            "Authorization": f"Bearer {sp_token}",
        }

        try:
            result = self.sdk.requests.delete(
                f"{self.sdk.cloud.endpoints.resource_manager}/{role_assignment_cloud_id}?api-version=2015-07-01",
                headers=headers,
                timeout=30,
            )
            result.raise_for_status()
            return result.json()

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not disable user. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error azure disable user")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not disable user. Request timed out.", exc_info=1,
            )
            raise ConnectionException("timout error azure disable user")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code, "azure application error disable user", exc_info=1,
            )
            raise UnknownServerException(
                result.status_code, f"azure application error disable user. {str(exc)}",
            )

    def create_tenant(self, payload: TenantCSPPayload):
        sp_token = self._get_root_provisioning_token()
        if sp_token is None:
            raise AuthenticationException("Could not resolve token for tenant creation")

        payload.password = token_urlsafe(16)
        create_tenant_body = payload.dict(by_alias=True)

        create_tenant_headers = {
            "Authorization": f"Bearer {sp_token}",
        }

        try:
            result = self.sdk.requests.post(
                f"{self.sdk.cloud.endpoints.resource_manager}providers/Microsoft.SignUp/createTenant?api-version=2020-01-01-preview",
                json=create_tenant_body,
                headers=create_tenant_headers,
                timeout=30,
            )
            result.raise_for_status()

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create tenant. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error creating tenant")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create tenant. Request timed out.", exc_info=1,
            )
            raise ConnectionException("timout error creating tenant")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error creating tenant",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error creating tenant. {str(exc)}",
            )

        result_dict = result.json()
        tenant_id = result_dict.get("tenantId")
        tenant_admin_username = f"{payload.user_id}@{payload.domain_name}.{self.config.get('OFFICE_365_DOMAIN')}"
        self.update_tenant_creds(
            tenant_id,
            KeyVaultCredentials(
                tenant_id=tenant_id,
                tenant_admin_username=tenant_admin_username,
                tenant_admin_password=payload.password,
            ),
        )

        return TenantCSPResult(domain_name=payload.domain_name, **result_dict)

    def create_billing_profile_creation(
        self, payload: BillingProfileCreationCSPPayload
    ):
        sp_token = self._get_root_provisioning_token()
        if sp_token is None:
            raise AuthenticationException(
                "Could not resolve token for billing profile creation"
            )

        create_billing_account_body = payload.dict(by_alias=True)

        create_billing_account_headers = {
            "Authorization": f"Bearer {sp_token}",
        }

        billing_account_create_url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Billing/billingAccounts/{payload.billing_account_name}/billingProfiles?api-version=2019-10-01-preview"

        try:
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

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create billing profile. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error creating billing profile")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create billing profile. Request timed out.", exc_info=1,
            )
            raise ConnectionException("timout error creating tenant")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error creating billing profile",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error creating billing profile. {str(exc)}",
            )

    def create_billing_profile_verification(
        self, payload: BillingProfileVerificationCSPPayload
    ):
        sp_token = self._get_root_provisioning_token()
        if sp_token is None:
            raise AuthenticationException(
                "Could not resolve token for billing profile validation"
            )

        auth_header = {
            "Authorization": f"Bearer {sp_token}",
        }
        try:
            result = self.sdk.requests.get(
                payload.billing_profile_verify_url, headers=auth_header, timeout=30,
            )
            result.raise_for_status()

            if result.status_code == 202:
                # 202 has location/retry after headers
                return BillingProfileCreationCSPResult(**result.headers)
            elif result.status_code == 200:
                return BillingProfileVerificationCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not verify billing profile creation. Connection Error",
                exc_info=1,
            )
            raise ConnectionException(
                "connection error creating billing profile verification"
            )
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not verify billing profile creation. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException(
                "timout error during billing profile verification"
            )
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error during billing profile verification",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error during billing profile verification. {str(exc)}",
            )

    def create_billing_profile_tenant_access(
        self, payload: BillingProfileTenantAccessCSPPayload
    ):
        sp_token = self._get_root_provisioning_token()
        request_body = {
            "properties": {
                "principalTenantId": payload.tenant_id,  # from tenant creation
                "principalId": payload.user_object_id,  # from tenant creationn
                "roleDefinitionId": f"/providers/Microsoft.Billing/billingAccounts/{payload.billing_account_name}/billingProfiles/{payload.billing_profile_name}/billingRoleDefinitions/40000000-aaaa-bbbb-cccc-100000000000",
            }
        }

        headers = {
            "Authorization": f"Bearer {sp_token}",
        }

        url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Billing/billingAccounts/{payload.billing_account_name}/billingProfiles/{payload.billing_profile_name}/createBillingRoleAssignment?api-version=2019-10-01-preview"
        try:
            result = self.sdk.requests.post(
                url, headers=headers, json=request_body, timeout=30,
            )
            result.raise_for_status()
            if result.status_code == 201:
                return BillingProfileTenantAccessCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create billing profile tenant access. Connection Error",
                exc_info=1,
            )
            raise ConnectionException(
                "connection error creating billing profile tenant access"
            )
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create billing profile tenant access. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException(
                "timout error creating billing profile tenant access"
            )
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error creating billing profile tenant access",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error creating billing profile tenant access. {str(exc)}",
            )

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

        try:
            result = self.sdk.requests.patch(
                url, headers=request_headers, json=request_body, timeout=30,
            )
            result.raise_for_status()

            if result.status_code == 202:
                # 202 has location/retry after headers
                return TaskOrderBillingCreationCSPResult(**result.headers)
            elif result.status_code == 200:
                return TaskOrderBillingVerificationCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create task order billing. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error creating task order billing")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create task order billing. Request timed out.", exc_info=1,
            )
            raise ConnectionException("timout error creating task order billing")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error creating task order billing",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error creating task order billing. {str(exc)}",
            )

    def create_task_order_billing_verification(
        self, payload: TaskOrderBillingVerificationCSPPayload
    ):
        sp_token = self._get_root_provisioning_token()
        if sp_token is None:
            raise AuthenticationException(
                "Could not resolve token for task order billing validation"
            )

        auth_header = {
            "Authorization": f"Bearer {sp_token}",
        }

        try:
            result = self.sdk.requests.get(
                payload.task_order_billing_verify_url, headers=auth_header, timeout=30,
            )
            result.raise_for_status()

            if result.status_code == 202:
                # 202 has location/retry after headers
                return TaskOrderBillingCreationCSPResult(**result.headers)
            elif result.status_code == 200:
                return TaskOrderBillingVerificationCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not verify task order billing. Connection Error", exc_info=1,
            )
            raise ConnectionException(
                "connection error during task order billing verification"
            )
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create verify task order billing. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException("timout error in task order billing verification")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error in task order billing verification",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error in task order billing verification. {str(exc)}",
            )

    def create_billing_instruction(self, payload: BillingInstructionCSPPayload):
        sp_token = self._get_root_provisioning_token()
        if sp_token is None:
            raise AuthenticationException(
                "Could not resolve token for task order billing validation"
            )

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

        try:
            result = self.sdk.requests.put(
                url, headers=auth_header, json=request_body, timeout=30
            )
            result.raise_for_status()
            return BillingInstructionCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create billing instructions. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error creating billing instructions")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create billing instructions. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException("timout error creating billing instructions")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error in creating billing instructions",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error in creating billing instructions. {str(exc)}",
            )

    def create_subscription(self, payload: SubscriptionCreationCSPPayload):
        sp_token = self._get_tenant_principal_token(payload.tenant_id)
        if sp_token is None:
            raise AuthenticationException(
                "Could not resolve token for subscription creation"
            )

        request_body = {
            "displayName": payload.display_name,
            "skuId": AZURE_SKU_ID,
            "managementGroupId": payload.parent_group_id,
        }

        url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Billing/billingAccounts/{payload.billing_account_name}/billingProfiles/{payload.billing_profile_name}/invoiceSections/{payload.invoice_section_name}/providers/Microsoft.Subscription/createSubscription?api-version=2019-10-01-preview"

        auth_header = {
            "Authorization": f"Bearer {sp_token}",
        }

        try:
            result = self.sdk.requests.put(
                url, headers=auth_header, json=request_body, timeout=30
            )
            result.raise_for_status()
            if result.status_code in [200, 202]:
                # 202 has location/retry after headers
                return SubscriptionCreationCSPResult(**result.headers, **result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create subscription. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error creating subscription")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create subscription. Request timed out.", exc_info=1,
            )
            raise ConnectionException("timout error creating subscription")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error creating subscription",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error creating subscription. {str(exc)}",
            )

    def create_subscription_creation(self, payload: SubscriptionCreationCSPPayload):
        return self.create_subscription(payload)

    def create_subscription_verification(
        self, payload: SubscriptionVerificationCSPPayload
    ):
        sp_token = self._get_tenant_principal_token(payload.tenant_id)
        if sp_token is None:
            raise AuthenticationException(
                "Could not resolve token for subscription verification"
            )

        auth_header = {
            "Authorization": f"Bearer {sp_token}",
        }

        try:
            result = self.sdk.requests.get(
                payload.subscription_verify_url, headers=auth_header, timeout=30
            )
            result.raise_for_status()

            # 202 has location/retry after headers
            return SuscriptionVerificationCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not verify subscription. Connection Error", exc_info=1,
            )
            raise ConnectionException(
                "connection error during subscription verification"
            )
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not verify subscription. Request timed out.", exc_info=1,
            )
            raise ConnectionException("timout error during subscription verification")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error during subscription verification",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error during subscription verification. {str(exc)}",
            )

    def create_product_purchase(self, payload: ProductPurchaseCSPPayload):
        sp_token = self._get_root_provisioning_token()
        if sp_token is None:
            raise AuthenticationException(
                "Could not resolve token for aad premium product purchase"
            )

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
        try:
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

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not purchase product. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error during product purchase")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not purchase product. Request timed out.", exc_info=1,
            )
            raise ConnectionException("timout error during product purchase")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error during product purchase",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error during product purchase. {str(exc)}",
            )

    def create_product_purchase_verification(
        self, payload: ProductPurchaseVerificationCSPPayload
    ):
        sp_token = self._get_root_provisioning_token()
        if sp_token is None:
            raise AuthenticationException(
                "Could not resolve token for aad premium product purchase validation"
            )

        auth_header = {
            "Authorization": f"Bearer {sp_token}",
        }
        try:
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

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not verify product purchase. Connection Error", exc_info=1,
            )
            raise ConnectionException(
                "connection error during product purchase verification"
            )
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not verify product purchase. Request timed out.", exc_info=1,
            )
            raise ConnectionException(
                "timout error during product purchase verification"
            )
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error during product purchase verification",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error during product purchase verification. {str(exc)}",
            )

    def create_tenant_admin_ownership(self, payload: TenantAdminOwnershipCSPPayload):
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

        url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Management/managementGroups/{payload.tenant_id}/providers/Microsoft.Authorization/roleAssignments/{assignment_guid}?api-version=2015-07-01"

        try:
            result = self.sdk.requests.put(
                url, headers=auth_header, json=request_body, timeout=30
            )
            result.raise_for_status()

            return TenantAdminOwnershipCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create tenant admin ownership. Connection Error",
                exc_info=1,
            )
            raise ConnectionException(
                "connection error creating tenant admin ownership"
            )
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create tenant admin ownership. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException("timout error creating tenant admin ownership")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error creating tenant admin ownership",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error creating tenant admin ownership. {str(exc)}",
            )

    def create_tenant_principal_ownership(
        self, payload: TenantPrincipalOwnershipCSPPayload
    ):
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

        url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Management/managementGroups/{payload.tenant_id}/providers/Microsoft.Authorization/roleAssignments/{assignment_guid}?api-version=2015-07-01"

        try:
            result = self.sdk.requests.put(
                url, headers=auth_header, json=request_body, timeout=30,
            )
            result.raise_for_status()
            return TenantPrincipalOwnershipCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create tenant principal ownership. Connection Error",
                exc_info=1,
            )
            raise ConnectionException(
                "connection error creating tenant principal ownership"
            )
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create tenant principal ownership. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException(
                "timout error creating tenant prinicpal ownership"
            )
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error creating tenant principal ownership",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error creating tenant principal ownership. {str(exc)}",
            )

    def create_tenant_principal_app(self, payload: TenantPrincipalAppCSPPayload):
        graph_token = self._get_tenant_admin_token(
            payload.tenant_id, self.graph_resource
        )
        if graph_token is None:
            raise AuthenticationException(
                "Could not resolve graph token for tenant admin"
            )

        request_body = {"displayName": "ATAT Remote Admin"}

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/v1.0/applications"

        try:
            result = self.sdk.requests.post(
                url, json=request_body, headers=auth_header, timeout=30
            )
            result.raise_for_status()
            return TenantPrincipalAppCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create tenant principal app. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error creating tenant principal app")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create tenant principal app. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException("timout error creating tenant principal app")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error creating tenant principal app",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error creating tenant principal app. {str(exc)}",
            )

    def create_tenant_principal(self, payload: TenantPrincipalCSPPayload):
        graph_token = self._get_tenant_admin_token(
            payload.tenant_id, self.graph_resource
        )
        if graph_token is None:
            raise AuthenticationException(
                "Could not resolve graph token for tenant admin"
            )

        request_body = {"appId": payload.principal_app_id}

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/beta/servicePrincipals"

        try:
            result = self.sdk.requests.post(
                url, json=request_body, headers=auth_header, timeout=30
            )
            result.raise_for_status()
            return TenantPrincipalCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create tenant principal. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error creating tenant principal")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create tenant principal. Request timed out.", exc_info=1,
            )
            raise ConnectionException("timout error creating tenant principal")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error creating tenant principal",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error creating tenant principal. {str(exc)}",
            )

    def create_tenant_principal_credential(
        self, payload: TenantPrincipalCredentialCSPPayload
    ):
        graph_token = self._get_tenant_admin_token(
            payload.tenant_id, self.graph_resource
        )
        if graph_token is None:
            raise AuthenticationException(
                "Could not resolve graph token for tenant admin"
            )

        request_body = {
            "passwordCredentials": [{"displayName": "ATAT Generated Password"}]
        }

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/v1.0/applications/{payload.principal_app_object_id}/addPassword"

        try:
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

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create tenant principal credential. Connection Error",
                exc_info=1,
            )
            raise ConnectionException(
                "connection error creating tenant principal credential"
            )
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create tenant principal credential. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException(
                "timout error creating tenant principal credential"
            )
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error creating tenant principal credential",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error creating tenant principal credential. {str(exc)}",
            )

    def create_admin_role_definition(self, payload: AdminRoleDefinitionCSPPayload):
        graph_token = self._get_tenant_admin_token(
            payload.tenant_id, self.graph_resource
        )
        if graph_token is None:
            raise AuthenticationException(
                "Could not resolve graph token for tenant admin"
            )

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/beta/roleManagement/directory/roleDefinitions"
        try:
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

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create admin role definition. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error creating admin role definition")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create admin role definition. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException("timout error creating admin role definition")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                response.status_code,
                "azure application error creating admin role definition",
                exc_info=1,
            )
            raise UnknownServerException(
                response.status_code,
                f"azure application error creating admin role definition. {str(exc)}",
            )

    def create_principal_admin_role(self, payload: PrincipalAdminRoleCSPPayload):
        graph_token = self._get_tenant_admin_token(
            payload.tenant_id, self.graph_resource
        )
        if graph_token is None:
            raise AuthenticationException(
                "Could not resolve graph token for tenant admin"
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

        try:
            result = self.sdk.requests.post(
                url, headers=auth_header, json=request_body, timeout=30
            )
            result.raise_for_status()
            return PrincipalAdminRoleCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create principal admin role. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error creating principal admin role")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create principal admin role. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException("timout error creating principal admin role")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error creating principal admin role",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error creating principal admin role. {str(exc)}",
            )

    def create_billing_owner(self, payload: BillingOwnerCSPPayload):
        graph_token = self._get_tenant_principal_token(
            payload.tenant_id, resource=self.graph_resource
        )
        if graph_token is None:
            raise AuthenticationException(
                "Could not resolve graph token for tenant admin"
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

        try:
            result = self.sdk.requests.post(url, headers=auth_header, json=request_body)
            result.raise_for_status()
        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not assign billing owner role. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error assigning billing owner role")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not assign billing owner role. Request timed out.", exc_info=1,
            )
            raise ConnectionException("timout error assigning billing owner role")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error assigning billing owner role",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error assigning billing owner role. {str(exc)}",
            )

        if result.ok:
            return True
        else:
            raise UserProvisioningException("Could not assign billing admin role")

    def _get_billing_owner_role(self, graph_token):
        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}/v1.0/directoryRoles"
        try:
            result = self.sdk.requests.get(url, headers=auth_header)
            result.raise_for_status()
        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not get billing owner role. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error getting billing owner role")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not get billing owner role. Request timed out.", exc_info=1,
            )
            raise ConnectionException("timout error getting billing owner role")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error getting billing owner role",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error getting billing owner role. {str(exc)}",
            )

        if result.ok:
            result = result.json()
            for role in result["value"]:
                if role["displayName"] == "Billing Administrator":
                    return role["id"]
        else:
            raise UserProvisioningException(
                "Could not find Billing Administrator role ID; role may not be enabled."
            )

    def _get_management_service_principal(self):
        # we really should be using graph.microsoft.com, but i'm getting
        # "expired token" errors for that
        # graph_resource = "https://graph.microsoft.com"
        graph_resource = "https://graph.windows.net"
        graph_creds = self._get_credential_obj(
            self._root_creds, resource=graph_resource
        )
        # I needed to set permissions for the graph.windows.net API before I
        # could get this to work.

        # how do we scope the graph client to the new subscription rather than
        # the cloud0 subscription? tenant id seems to be separate from subscription id
        graph_client = self.sdk.graphrbac.GraphRbacManagementClient(
            graph_creds, self._root_creds.get("tenant_id")
        )

        # do we need to create a new application to manage each subscripition
        # or should we manage access to each subscription from a single service
        # principal with multiple role assignments?
        app_display_name = "?"  # name should reflect the subscription it exists
        app_create_param = self.sdk.graphrbac.models.ApplicationCreateParameters(
            display_name=app_display_name
        )

        # we need the appropriate perms here:
        # https://docs.microsoft.com/en-us/graph/api/application-post-applications?view=graph-rest-beta&tabs=http
        # https://docs.microsoft.com/en-us/graph/permissions-reference#microsoft-graph-permission-names
        # set app perms in app registration portal
        # https://docs.microsoft.com/en-us/graph/auth-v2-service#2-configure-permissions-for-microsoft-graph
        app: self.sdk.graphrbac.models.Application = graph_client.applications.create(
            app_create_param
        )

        # create a new service principle for the new application, which should be scoped
        # to the new subscription
        app_id = app.app_id
        sp_create_params = self.sdk.graphrbac.models.ServicePrincipalCreateParameters(
            app_id=app_id, account_enabled=True
        )

        service_principal = graph_client.service_principals.create(sp_create_params)

        return service_principal

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
        if graph_token is None:
            raise AuthenticationException(
                "Could not resolve graph token for tenant admin"
            )

        result = self._create_active_directory_user(graph_token, payload)
        self._update_active_directory_user_email(graph_token, result.id, payload)

        return result

    def _create_active_directory_user(self, graph_token, payload):
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

        url = f"{self.graph_resource}v1.0/users"

        try:
            result = self.sdk.requests.post(
                url, headers=auth_header, json=request_body, timeout=30
            )
            result.raise_for_status()

            return UserCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not create active directory user. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error creating active directory user")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not create active directory user. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException("timout error creating active directory user")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error creating active directory user",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error creating active directory user. {str(exc)}",
            )

    def _update_active_directory_user_email(self, graph_token, user_id, payload):
        request_body = {"otherMails": [payload.email]}

        auth_header = {
            "Authorization": f"Bearer {graph_token}",
        }

        url = f"{self.graph_resource}v1.0/users/{user_id}"

        try:
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

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not update active directory user email. Connection Error",
                exc_info=1,
            )
            raise ConnectionException(
                "connection error updating active directory user email"
            )
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not update active directory user email. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException(
                "timout error updating active directory user email"
            )
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error updating active directory user email",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error updating active directory user email. {str(exc)}",
            )

    def create_user_role(self, payload: UserRoleCSPPayload):
        graph_token = self._get_tenant_principal_token(payload.tenant_id)
        if graph_token is None:
            raise AuthenticationException(
                "Could not resolve graph token for tenant admin"
            )

        role_guid = self.roles[payload.role]
        role_definition_id = f"/providers/Microsoft.Management/managementGroups/{payload.management_group_id}/providers/Microsoft.Authorization/roleDefinitions/{role_guid}"

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

        url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Management/managementGroups/{payload.management_group_id}/providers/Microsoft.Authorization/roleAssignments/{assignment_guid}?api-version=2015-07-01"

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
        return self._get_up_token_for_resource(
            creds.tenant_admin_username,
            creds.tenant_admin_password,
            tenant_id,
            resource,
        )

    def _get_root_provisioning_token(self):
        creds = self._source_creds()
        return self._get_sp_token(
            creds.root_tenant_id, creds.root_sp_client_id, creds.root_sp_key
        )

    def _get_sp_token(self, tenant_id, client_id, secret_key, resource=None):
        context = self.sdk.adal.AuthenticationContext(
            f"{self.sdk.cloud.endpoints.active_directory}/{tenant_id}"
        )

        resource = resource or self.sdk.cloud.endpoints.resource_manager
        # TODO: handle failure states here
        token_response = context.acquire_token_with_client_credentials(
            resource, client_id, secret_key
        )

        return token_response.get("accessToken", None)

    def _get_up_token_for_resource(self, username, password, tenant_id, resource):

        context = self.sdk.adal.AuthenticationContext(
            f"{self.sdk.cloud.endpoints.active_directory}/{tenant_id}"
        )

        # TODO: handle failure states here
        token_response = context.acquire_token_with_username_password(
            resource, username, password, self.ps_client_id
        )

        return token_response.get("accessToken", None)

    def _get_credential_obj(self, creds, resource=None):
        return self.sdk.credentials.ServicePrincipalCredentials(
            client_id=creds.get("client_id"),
            secret=creds.get("secret_key"),
            tenant=creds.get("tenant_id"),
            resource=resource,
            cloud_environment=self.sdk.cloud,
        )

    def _get_client_secret_credential_obj(self):
        creds = self._source_creds()
        return self.sdk.identity.ClientSecretCredential(
            tenant_id=creds.tenant_id,
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
        creds = self._source_creds(tenant_id)
        return self._get_sp_token(
            creds.tenant_id,
            creds.tenant_sp_client_id,
            creds.tenant_sp_key,
            resource=resource,
        )

    def _get_elevated_management_token(self, tenant_id):
        mgmt_token = self._get_tenant_admin_token(
            tenant_id, self.sdk.cloud.endpoints.resource_manager
        )
        if mgmt_token is None:
            raise AuthenticationException(
                "Failed to resolve management token for tenant admin"
            )

        auth_header = {
            "Authorization": f"Bearer {mgmt_token}",
        }
        url = f"{self.sdk.cloud.endpoints.resource_manager}/providers/Microsoft.Authorization/elevateAccess?api-version=2016-07-01"
        try:
            result = self.sdk.requests.post(url, headers=auth_header, timeout=30)
            result.raise_for_status()
            if not result.ok:
                raise AuthenticationException("Failed to elevate access")

            return mgmt_token

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not get elevated management token. Connection Error",
                exc_info=1,
            )
            raise ConnectionException(
                "connection error getting elevated management token"
            )
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not get elevated management token. Request timed out.",
                exc_info=1,
            )
            raise ConnectionException("timout error getting elevated management token")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error getting elevated management token",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error getting elevated management token. {str(exc)}",
            )

    def _source_creds(self, tenant_id=None) -> KeyVaultCredentials:
        if tenant_id:
            return self._source_tenant_creds(tenant_id)
        else:
            return KeyVaultCredentials(
                root_tenant_id=self._root_creds.get("tenant_id"),
                root_sp_client_id=self._root_creds.get("client_id"),
                root_sp_key=self._root_creds.get("secret_key"),
            )

    def update_tenant_creds(self, tenant_id, secret: KeyVaultCredentials):
        hashed = sha256_hex(tenant_id)
        curr_secrets = self._source_tenant_creds(tenant_id)
        updated_secrets = curr_secrets.merge_credentials(secret)
        self.set_secret(hashed, json.dumps(updated_secrets.dict()))
        return updated_secrets

    def _source_tenant_creds(self, tenant_id) -> KeyVaultCredentials:
        hashed = sha256_hex(tenant_id)
        raw_creds = self.get_secret(hashed)
        return KeyVaultCredentials(**json.loads(raw_creds))

    def get_reporting_data(self, payload: ReportingCSPPayload):
        """
        Queries the Cost Management API for an invoice section's raw reporting data

        We query at the invoiceSection scope. The full scope path is passed in
        with the payload at the `invoice_section_id` key.
        """
        creds = self._source_tenant_creds(payload.tenant_id)
        token = self._get_sp_token(
            payload.tenant_id, creds.tenant_sp_client_id, creds.tenant_sp_key
        )

        if not token:
            raise AuthenticationException("Could not retrieve tenant access token")

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
        try:
            result = self.sdk.requests.post(
                f"{self.sdk.cloud.endpoints.resource_manager}{payload.invoice_section_id}{cost_mgmt_url}",
                json=request_body,
                headers=headers,
                timeout=30,
            )
            result.raise_for_status()
            if result.ok:
                return CostManagementQueryCSPResult(**result.json())

        except self.sdk.requests.exceptions.ConnectionError:
            app.logger.error(
                f"Could not get reporting data. Connection Error", exc_info=1,
            )
            raise ConnectionException("connection error getting reporting data")
        except self.sdk.requests.exceptions.Timeout:
            app.logger.error(
                f"Could not get reporting data. Request timed out.", exc_info=1,
            )
            raise ConnectionException("timout error getting reporting data")
        except self.sdk.requests.exceptions.HTTPError as exc:
            app.logger.error(
                result.status_code,
                "azure application error getting reporting data",
                exc_info=1,
            )
            raise UnknownServerException(
                result.status_code,
                f"azure application error getting reporting data. {str(exc)}",
            )

    def _get_calculator_creds(self):
        authority = f"{self.sdk.cloud.endpoints.active_directory}/{self.tenant_id}"
        context = self.sdk.adal.AuthenticationContext(authority=authority)
        response = context.acquire_token_with_client_credentials(
            self.config.get("AZURE_CALC_RESOURCE"),
            self.config.get("AZURE_CALC_CLIENT_ID"),
            self.config.get("AZURE_CALC_SECRET"),
        )
        return response.get("accessToken")

    def get_calculator_url(self):
        calc_access_token = self._get_calculator_creds()
        return f"{self.config.get('AZURE_CALC_URL')}?access_token={calc_access_token}"
