import contextlib
from atat.domain.csp.cloud.azure_cloud_provider import AzureCloudProvider
from atat.domain.csp.cloud.exceptions import UnknownServerException
from atat.domain.csp.cloud.mock_cloud_provider import MockCloudProvider
from atat.domain.csp.cloud.models import *
from typing import Dict, Union
from uuid import uuid4
from operator import itemgetter


@contextlib.contextmanager
def monkeypatched(object_, name, patch):
    """ Temporarily monkeypatches an object. """

    pre_patched_value = getattr(object_, name)
    setattr(object_, name, patch)
    yield object_
    setattr(object_, name, pre_patched_value)


HYBRID_PREFIX = "Hybrid ::"


class HybridCloudProvider(object):
    def __init__(self, azure: AzureCloudProvider, mock: MockCloudProvider):
        self.azure = azure
        self.mock = mock
        self.tenant_id = None

    def create_tenant(self, payload: TenantCSPPayload) -> TenantCSPResult:
        """In this step, we store a tenant ID with a username and password
        provided to the application ahead of time. Normally the tenant is
        created through API calls to Azure, however for the hybrid mock we
        will generate and store a tenant with a simple generated UUID string
        instead.
        """

        # This is the username and password for the primary point of contact
        # for a portfolio. These are normally generated for the tenant, but
        # but here we just inject existing and valid credentials.
        tenant_admin_username = self.azure.config["AZURE_TENANT_ADMIN_USERNAME"]
        tenant_admin_password = self.azure.config["AZURE_TENANT_ADMIN_PASSWORD"]
        user_object_id = self.azure.config["AZURE_USER_OBJECT_ID"]

        self.tenant_id = str(uuid4())

        # This is our mocked result of what would have been the API call to
        # create a tenant.
        result_dict = {
            "tenant_id": self.tenant_id,
            "user_id": "HybridCSPIntegrationTestUser",
            "user_object_id": user_object_id,
            "tenant_admin_username": tenant_admin_username,
            "tenant_admin_password": tenant_admin_password,
        }

        # Here we use the tenant id as a KeyVault key to store the primary
        # point of contact credentials.
        self.azure.create_tenant_creds(
            self.tenant_id,
            KeyVaultCredentials(
                root_tenant_id=self.azure.root_tenant_id,
                root_sp_client_id=self.azure.client_id,
                root_sp_key=self.azure.secret_key,
                tenant_id=self.azure.root_tenant_id,
                tenant_admin_username=tenant_admin_username,
                tenant_admin_password=tenant_admin_password,
            ),
        )

        return TenantCSPResult(domain_name="dancorriganpromptworks", **result_dict)

    def create_billing_profile_creation(
        self, payload: BillingProfileCreationCSPPayload
    ) -> Union[BillingProfileCreationCSPResult, BillingProfileVerificationCSPResult]:
        return self.mock.create_billing_profile_creation(payload)

    def create_billing_profile_verification(
        self, payload: BillingProfileVerificationCSPPayload
    ) -> Union[BillingProfileCreationCSPResult, BillingProfileVerificationCSPResult]:

        return self.mock.create_billing_profile_verification(payload)

    def create_billing_profile_tenant_access(
        self, payload: BillingProfileTenantAccessCSPPayload
    ) -> BillingProfileTenantAccessCSPResult:
        return self.mock.create_billing_profile_tenant_access(payload)

    def create_task_order_billing_creation(
        self, payload: TaskOrderBillingCreationCSPPayload
    ) -> Union[
        TaskOrderBillingCreationCSPResult, TaskOrderBillingVerificationCSPResult
    ]:
        return self.mock.create_task_order_billing_creation(payload)

    def create_task_order_billing_verification(
        self, payload: TaskOrderBillingVerificationCSPPayload
    ) -> Union[
        TaskOrderBillingCreationCSPResult, TaskOrderBillingVerificationCSPResult
    ]:
        return self.mock.create_task_order_billing_verification(payload)

    def create_billing_instruction(
        self, payload: BillingInstructionCSPPayload
    ) -> BillingInstructionCSPResult:
        return self.mock.create_billing_instruction(payload)

    def create_product_purchase(
        self, payload: ProductPurchaseCSPPayload
    ) -> Union[ProductPurchaseCSPResult, ProductPurchaseVerificationCSPResult]:
        return self.mock.create_product_purchase(payload)

    def create_product_purchase_verification(
        self, payload: ProductPurchaseVerificationCSPPayload
    ) -> Union[ProductPurchaseCSPResult, ProductPurchaseVerificationCSPResult]:
        return self.mock.create_product_purchase_verification(payload)

    def create_tenant_principal_app(
        self, payload: TenantPrincipalAppCSPPayload
    ) -> TenantPrincipalAppCSPResult:
        with monkeypatched(
            self.azure,
            "tenant_principal_app_display_name",
            f"{HYBRID_PREFIX} {payload.display_name} :: ATAT Remote Admin",
        ):
            return self.azure.create_tenant_principal_app(payload)

    def create_tenant_principal(
        self, payload: TenantPrincipalCSPPayload
    ) -> TenantPrincipalCSPResult:
        return self.azure.create_tenant_principal(payload)

    def create_tenant_principal_credential(
        self, payload: TenantPrincipalCredentialCSPPayload
    ) -> TenantPrincipalCredentialCSPResult:
        token = self.azure._get_tenant_admin_token(
            payload.tenant_id, self.azure.graph_resource + "/.default"
        )

        original_update_tenant_creds = self.azure.update_tenant_creds

        def mocked_update_tenant_creds(tenant_id, creds):
            """Necessary to ensure the root tenant id credentials are saved in
            KeyVault at the end of this stage.
            """
            creds.tenant_id = self.azure.root_tenant_id
            original_update_tenant_creds(tenant_id, creds)

        with monkeypatched(self.azure, "_get_tenant_admin_token", lambda *_a: token):
            with monkeypatched(
                self.azure, "update_tenant_creds", mocked_update_tenant_creds
            ):
                return self.azure.create_tenant_principal_credential(payload)

    def create_admin_role_definition(
        self, payload: AdminRoleDefinitionCSPPayload
    ) -> AdminRoleDefinitionCSPResult:
        return self.azure.create_admin_role_definition(payload)

    def create_principal_admin_role(
        self, payload: PrincipalAdminRoleCSPPayload
    ) -> PrincipalAdminRoleCSPResult:
        return self.azure.create_principal_admin_role(payload)

    def create_initial_mgmt_group(
        self, payload: InitialMgmtGroupCSPPayload
    ) -> InitialMgmtGroupCSPResult:
        payload.tenant_id = self.azure.root_tenant_id
        payload.display_name = f"{HYBRID_PREFIX} {payload.display_name}"
        return self.azure.create_initial_mgmt_group(payload)

    def create_initial_mgmt_group_verification(
        self, payload: InitialMgmtGroupVerificationCSPPayload
    ) -> InitialMgmtGroupVerificationCSPResult:
        payload.tenant_id = self.azure.root_tenant_id
        return self.azure.create_initial_mgmt_group_verification(payload)

    def create_tenant_admin_ownership(
        self, payload: TenantAdminOwnershipCSPPayload
    ) -> TenantAdminOwnershipCSPResult:
        """For this step, we needed to be able to retrieve the elevated management
        token from KeyVault with the original tenant id, but make the role assignment
        request with the root credentials.
        """

        token = self.azure._get_elevated_management_token(payload.tenant_id)
        payload.tenant_id = self.azure.root_tenant_id
        with monkeypatched(
            self.azure, "_get_elevated_management_token", lambda _: token
        ):
            try:
                return self.azure.create_tenant_admin_ownership(payload)
            except UnknownServerException:
                return TenantAdminOwnershipCSPResult(
                    id=self.azure.config["AZURE_ADMIN_ROLE_ASSIGNMENT_ID"]
                )

    def create_tenant_principal_ownership(
        self, payload: TenantPrincipalOwnershipCSPPayload
    ) -> TenantPrincipalOwnershipCSPResult:

        """For this step, we needed to be able to retrieve the elevated
        management token from KeyVault with the original tenant id, but make
        the tenant principal ownership request with the root credentials.
        """

        token = self.azure._get_elevated_management_token(payload.tenant_id)
        payload.tenant_id = self.azure.root_tenant_id
        with monkeypatched(
            self.azure, "_get_elevated_management_token", lambda _: token
        ):
            return self.azure.create_tenant_principal_ownership(payload)

    def create_billing_owner(
        self, payload: BillingOwnerCSPPayload
    ) -> BillingOwnerCSPResult:
        token = self.azure._get_tenant_principal_token(
            payload.tenant_id, scope=self.azure.graph_resource + "/.default"
        )
        payload.tenant_id = self.azure.root_tenant_id
        with monkeypatched(
            self.azure, "_get_tenant_principal_token", lambda *a, **kw: token
        ):
            payload.display_name = f"{HYBRID_PREFIX} {payload.display_name} :: Billing"
            return self.azure.create_billing_owner(payload)

    def create_tenant_admin_credential_reset(
        self, payload: TenantAdminCredentialResetCSPPayload
    ) -> TenantAdminCredentialResetCSPResult:
        return self.mock.create_tenant_admin_credential_reset(payload)

    def create_policies(self, payload: PoliciesCSPPayload) -> PoliciesCSPResult:
        return self.azure.create_policies(payload)

    def create_application(self, payload):
        payload.display_name = f"{HYBRID_PREFIX} {payload.display_name}"
        return self.azure.create_application(payload)

    def create_environment(
        self, payload: EnvironmentCSPPayload
    ) -> EnvironmentCSPResult:
        payload.display_name = f"{HYBRID_PREFIX} {payload.display_name}"
        return self.azure.create_environment(payload)

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
        return self.azure.create_user(payload)

    def create_user_role(self, payload: UserRoleCSPPayload) -> UserRoleCSPResult:
        return self.azure.create_user_role(payload)

    def disable_user(self, tenant_id: str, role_assignment_cloud_id: str) -> Dict:
        return self.azure.disable_user(tenant_id, role_assignment_cloud_id)

    def get_reporting_data(self, payload: CostManagementQueryCSPPayload):
        billing_account_id, billing_profile_id, invoice_section_id = itemgetter(
            "AZURE_BILLING_ACCOUNT_NAME",
            "AZURE_BILLING_PROFILE_ID",
            "AZURE_INVOICE_SECTION_ID",
        )(self.azure.config)

        isi = f"/providers/Microsoft.Billing/billingAccounts/{billing_account_id}/billingProfiles/{billing_profile_id}/invoiceSections/{invoice_section_id}"
        payload.invoice_section_id = isi

        return self.azure.get_reporting_data(payload)

    def create_subscription(self, payload: SubscriptionCreationCSPPayload):
        # TODO: This will need to be updated to use the azure function.  The same with
        # "create_subscription_creation" and "create_subscription_verification".  Additionally,
        # the payload display_name will have to be prepended with the hybrid prefix.
        #
        # Example code:
        # payload.display_name = f"{HYBRID_PREFIX} {payload.display_name}"
        # return self.azure.create_subscription(payload)
        return self.mock.create_subscription(payload)

    def create_subscription_creation(self, payload: SubscriptionCreationCSPPayload):
        return self.mock.create_subscription_creation(payload)

    def create_subscription_verification(
        self, payload: SubscriptionVerificationCSPPayload
    ):
        return self.mock.create_subscription_verification(payload)
