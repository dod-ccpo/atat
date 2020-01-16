import re
from typing import Dict
from uuid import uuid4

from pydantic import BaseModel

from atst.models.user import User
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole


class GeneralCSPException(Exception):
    pass


class OperationInProgressException(GeneralCSPException):
    """Throw this for instances when the CSP reports that the current entity is already
    being operated on/created/deleted/etc
    """

    def __init__(self, operation_desc):
        self.operation_desc = operation_desc

    @property
    def message(self):
        return "An operation for this entity is already in progress: {}".format(
            self.operation_desc
        )


class AuthenticationException(GeneralCSPException):
    """Throw this for instances when there is a problem with the auth credentials:
    * Missing credentials
    * Incorrect credentials
    * Other credential problems
    """

    def __init__(self, auth_error):
        self.auth_error = auth_error

    @property
    def message(self):
        return "An error occurred with authentication: {}".format(self.auth_error)


class AuthorizationException(GeneralCSPException):
    """Throw this for instances when the current credentials are not authorized
    for the current action.
    """

    def __init__(self, auth_error):
        self.auth_error = auth_error

    @property
    def message(self):
        return "An error occurred with authorization: {}".format(self.auth_error)


class ConnectionException(GeneralCSPException):
    """A general problem with the connection, timeouts or unresolved endpoints
    """

    def __init__(self, connection_error):
        self.connection_error = connection_error

    @property
    def message(self):
        return "Could not connect to cloud provider: {}".format(self.connection_error)


class UnknownServerException(GeneralCSPException):
    """An error occured on the CSP side (5xx) and we don't know why
    """

    def __init__(self, server_error):
        self.server_error = server_error

    @property
    def message(self):
        return "A server error occured: {}".format(self.server_error)


class EnvironmentCreationException(GeneralCSPException):
    """If there was an error in creating the environment
    """

    def __init__(self, env_identifier, reason):
        self.env_identifier = env_identifier
        self.reason = reason

    @property
    def message(self):
        return "The envionment {} couldn't be created: {}".format(
            self.env_identifier, self.reason
        )


class UserProvisioningException(GeneralCSPException):
    """Failed to provision a user
    """

    def __init__(self, env_identifier, user_identifier, reason):
        self.env_identifier = env_identifier
        self.user_identifier = user_identifier
        self.reason = reason

    @property
    def message(self):
        return "Failed to create user {} for environment {}: {}".format(
            self.user_identifier, self.env_identifier, self.reason
        )


class UserRemovalException(GeneralCSPException):
    """Failed to remove a user
    """

    def __init__(self, user_csp_id, reason):
        self.user_csp_id = user_csp_id
        self.reason = reason

    @property
    def message(self):
        return "Failed to suspend or delete user {}: {}".format(
            self.user_csp_id, self.reason
        )


class BaselineProvisionException(GeneralCSPException):
    """If there's any issues standing up whatever is required
    for an environment baseline
    """

    def __init__(self, env_identifier, reason):
        self.env_identifier = env_identifier
        self.reason = reason

    @property
    def message(self):
        return "Could not complete baseline provisioning for environment ({}): {}".format(
            self.env_identifier, self.reason
        )


class BaseCSPPayload(BaseModel):
    # {"username": "mock-cloud", "pass": "shh"}
    creds: Dict


class TenantCSPPayload(BaseCSPPayload):
    user_id: str
    password: str
    domain_name: str
    first_name: str
    last_name: str
    country_code: str
    password_recovery_email_address: str


class TenantCSPResult(BaseModel):
    user_id: str
    tenant_id: str
    user_object_id: str


class BillingProfileAddress(BaseModel):
    address: Dict
    """
    "address": {
        "firstName": "string",
        "lastName": "string",
        "companyName": "string",
        "addressLine1": "string",
        "addressLine2": "string",
        "addressLine3": "string",
        "city": "string",
        "region": "string",
        "country": "string",
        "postalCode": "string"
    },
    """


class BillingProfileCLINBudget(BaseModel):
    clinBudget: Dict
    """
        "clinBudget": {
            "amount": 0,
            "startDate": "2019-12-18T16:47:40.909Z",
            "endDate": "2019-12-18T16:47:40.909Z",
            "externalReferenceId": "string"
        }
    """


class BillingProfileCSPPayload(
    BaseCSPPayload, BillingProfileAddress, BillingProfileCLINBudget
):
    displayName: str
    poNumber: str
    invoiceEmailOptIn: str

    """
    {
        "displayName": "string",
        "poNumber": "string",
        "address": {
            "firstName": "string",
            "lastName": "string",
            "companyName": "string",
            "addressLine1": "string",
            "addressLine2": "string",
            "addressLine3": "string",
            "city": "string",
            "region": "string",
            "country": "string",
            "postalCode": "string"
        },
        "invoiceEmailOptIn": true,
        Note: These last 2 are also the body for adding/updating new TOs/clins
        "enabledAzurePlans": [
            {
            "skuId": "string"
            }
        ],
        "clinBudget": {
            "amount": 0,
            "startDate": "2019-12-18T16:47:40.909Z",
            "endDate": "2019-12-18T16:47:40.909Z",
            "externalReferenceId": "string"
        }
    }
    """


class CloudProviderInterface:
    def root_creds(self) -> Dict:
        raise NotImplementedError()

    def create_environment(
        self, auth_credentials: Dict, user: User, environment: Environment
    ) -> str:
        """Create a new environment in the CSP.

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            user -- ATAT user authorizing the environment creation
            environment -- ATAT Environment model

        Returns:
            string: ID of created environment

        Raises:
            AuthenticationException: Problem with the credentials
            AuthorizationException: Credentials not authorized for current action(s)
            ConnectionException: Issue with the CSP API connection
            UnknownServerException: Unknown issue on the CSP side
            EnvironmentExistsException: Environment already exists and has been created
        """
        raise NotImplementedError()

    def create_atat_admin_user(
        self, auth_credentials: Dict, csp_environment_id: str
    ) -> Dict:
        """Creates a new, programmatic user in the CSP. Grants this user full permissions to administer
        the CSP.

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            csp_environment_id -- ID of the CSP Environment the admin user should be created in

        Returns:
            object: Object representing new remote admin user, including credentials
            Something like:
            {
                "user_id": string,
                "credentials": dict, # structure TBD based on csp
            }

        Raises:
            AuthenticationException: Problem with the credentials
            AuthorizationException: Credentials not authorized for current action(s)
            ConnectionException: Issue with the CSP API connection
            UnknownServerException: Unknown issue on the CSP side
            UserProvisioningException: Problem creating the root user
        """
        raise NotImplementedError()

    def create_or_update_user(
        self, auth_credentials: Dict, user_info: EnvironmentRole, csp_role_id: str
    ) -> str:
        """Creates a user or updates an existing user's role.

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            user_info -- instance of EnvironmentRole containing user data
                         if it has a csp_user_id it will try to update that user
            csp_role_id -- The id of the role the user should be given in the CSP

        Returns:
            string: Returns the interal csp_user_id of the created/updated user account

        Raises:
            AuthenticationException: Problem with the credentials
            AuthorizationException: Credentials not authorized for current action(s)
            ConnectionException: Issue with the CSP API connection
            UnknownServerException: Unknown issue on the CSP side
            UserProvisioningException: User couldn't be created or modified
        """
        raise NotImplementedError()

    def disable_user(self, auth_credentials: Dict, csp_user_id: str) -> bool:
        """Revoke all privileges for a user. Used to prevent user access while a full
        delete is being processed.

        Arguments:
            auth_credentials -- Object containing CSP account credentials
            csp_user_id -- CSP internal user identifier

        Returns:
            bool -- True on success

        Raises:
            AuthenticationException: Problem with the credentials
            AuthorizationException: Credentials not authorized for current action(s)
            ConnectionException: Issue with the CSP API connection
            UnknownServerException: Unknown issue on the CSP side
            UserRemovalException: User couldn't be suspended
        """
        raise NotImplementedError()

    def get_calculator_url(self) -> str:
        """Returns the calculator url for the CSP.
        This will likely be a static property elsewhere once a CSP is chosen.
        """
        raise NotImplementedError()

    def get_environment_login_url(self, environment) -> str:
        """Returns the login url for a given environment
        This may move to be a computed property on the Environment domain object
        """
        raise NotImplementedError()


class MockCloudProvider(CloudProviderInterface):

    # TODO: All of these constants
    AUTHENTICATION_EXCEPTION = AuthenticationException("Authentication failure.")
    AUTHORIZATION_EXCEPTION = AuthorizationException("Not authorized.")
    NETWORK_EXCEPTION = ConnectionException("Network failure.")
    SERVER_EXCEPTION = UnknownServerException("Not our fault.")

    SERVER_FAILURE_PCT = 1
    NETWORK_FAILURE_PCT = 7
    ENV_CREATE_FAILURE_PCT = 12
    ATAT_ADMIN_CREATE_FAILURE_PCT = 12
    UNAUTHORIZED_RATE = 2

    def __init__(
        self, config, with_delay=True, with_failure=True, with_authorization=True
    ):
        from time import sleep
        import random

        self._with_delay = with_delay
        self._with_failure = with_failure
        self._with_authorization = with_authorization
        self._sleep = sleep
        self._random = random

    def root_creds(self):
        return self._auth_credentials

    def create_environment(self, auth_credentials, user, environment):
        self._authorize(auth_credentials)

        self._delay(1, 5)
        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)
        self._maybe_raise(
            self.ENV_CREATE_FAILURE_PCT,
            EnvironmentCreationException(
                environment.id, "Could not create environment."
            ),
        )

        csp_environment_id = self._id()

        self._delay(1, 5)
        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)
        self._maybe_raise(
            self.ATAT_ADMIN_CREATE_FAILURE_PCT,
            BaselineProvisionException(
                csp_environment_id, "Could not create environment baseline."
            ),
        )
        self._maybe_raise(self.UNAUTHORIZED_RATE, self.AUTHORIZATION_EXCEPTION)

        return csp_environment_id

    def create_atat_admin_user(self, auth_credentials, csp_environment_id):
        self._authorize(auth_credentials)

        self._delay(1, 5)
        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)
        self._maybe_raise(
            self.ATAT_ADMIN_CREATE_FAILURE_PCT,
            UserProvisioningException(
                csp_environment_id, "atat_admin", "Could not create admin user."
            ),
        )

        self._maybe_raise(self.UNAUTHORIZED_RATE, self.AUTHORIZATION_EXCEPTION)

        return {"id": self._id(), "credentials": self._auth_credentials}

    def create_tenant(self, payload):
        """
        payload is an instance of TenantCSPPayload data class
        """

        self._authorize(payload.creds)

        self._delay(1, 5)

        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)
        self._maybe_raise(self.UNAUTHORIZED_RATE, self.AUTHORIZATION_EXCEPTION)
        # return tenant id, tenant owner id and tenant owner object id from:
        response = {"tenantId": "string", "userId": "string", "objectId": "string"}
        return {
            "tenant_id": response["tenantId"],
            "user_id": response["userId"],
            "user_object_id": response["objectId"],
        }

    def create_billing_profile(self, creds, tenant_admin_details, billing_owner_id):
        # call billing profile creation endpoint, specifying owner
        # Payload:
        """
        {
            "displayName": "string",
            "poNumber": "string",
            "address": {
                "firstName": "string",
                "lastName": "string",
                "companyName": "string",
                "addressLine1": "string",
                "addressLine2": "string",
                "addressLine3": "string",
                "city": "string",
                "region": "string",
                "country": "string",
                "postalCode": "string"
            },
            "invoiceEmailOptIn": true,
            Note: These last 2 are also the body for adding/updating new TOs/clins
            "enabledAzurePlans": [
                {
                "skuId": "string"
                }
            ],
            "clinBudget": {
                "amount": 0,
                "startDate": "2019-12-18T16:47:40.909Z",
                "endDate": "2019-12-18T16:47:40.909Z",
                "externalReferenceId": "string"
            }
        }
        """
        # response will be mostly the same as the body, but we only really care about the id
        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)
        self._maybe_raise(self.UNAUTHORIZED_RATE, self.AUTHORIZATION_EXCEPTION)

        response = {"id": "string"}
        return {"billing_profile_id": response["id"]}

    def create_or_update_user(self, auth_credentials, user_info, csp_role_id):
        self._authorize(auth_credentials)

        self._delay(1, 5)
        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)
        self._maybe_raise(
            self.ATAT_ADMIN_CREATE_FAILURE_PCT,
            UserProvisioningException(
                user_info.environment.id,
                user_info.application_role.user_id,
                "Could not create user.",
            ),
        )

        self._maybe_raise(self.UNAUTHORIZED_RATE, self.AUTHORIZATION_EXCEPTION)
        return self._id()

    def disable_user(self, auth_credentials, csp_user_id):
        self._authorize(auth_credentials)
        self._maybe_raise(self.NETWORK_FAILURE_PCT, self.NETWORK_EXCEPTION)
        self._maybe_raise(self.SERVER_FAILURE_PCT, self.SERVER_EXCEPTION)

        self._maybe_raise(
            self.ATAT_ADMIN_CREATE_FAILURE_PCT,
            UserRemovalException(csp_user_id, "Could not disable user."),
        )

        return self._maybe(12)

    def get_calculator_url(self):
        return "https://www.rackspace.com/en-us/calculator"

    def get_environment_login_url(self, environment):
        """Returns the login url for a given environment
        """
        return "https://www.mycloud.com/my-env-login"

    def _id(self):
        return uuid4().hex

    def _delay(self, min_secs, max_secs):
        if self._with_delay:
            duration = self._random.randrange(min_secs, max_secs)
            self._sleep(duration)

    def _maybe(self, pct):
        return not self._with_failure or self._random.randrange(0, 100) < pct

    def _maybe_raise(self, pct, exc):
        if self._with_failure and self._maybe(pct):
            raise exc

    @property
    def _auth_credentials(self):
        return {"username": "mock-cloud", "pass": "shh"}

    def _authorize(self, credentials):
        self._delay(1, 5)
        if self._with_authorization and credentials != self._auth_credentials:
            raise self.AUTHENTICATION_EXCEPTION


AZURE_ENVIRONMENT = "AZURE_PUBLIC_CLOUD"  # TBD
AZURE_SKU_ID = "?"  # probably a static sku specific to ATAT/JEDI
SUBSCRIPTION_ID_REGEX = re.compile(
    "subscriptions\/([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})",
    re.I,
)

# This needs to be a fully pathed role definition identifier, not just a UUID
REMOTE_ROOT_ROLE_DEF_ID = "/providers/Microsoft.Authorization/roleDefinitions/00000000-0000-4000-8000-000000000000"


class AzureSDKProvider(object):
    def __init__(self):
        from azure.mgmt import subscription, authorization
        import azure.graphrbac as graphrbac
        import azure.common.credentials as credentials
        from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD

        self.subscription = subscription
        self.authorization = authorization
        self.graphrbac = graphrbac
        self.credentials = credentials
        # may change to a JEDI cloud
        self.cloud = AZURE_PUBLIC_CLOUD


class AzureCloudProvider(CloudProviderInterface):
    def __init__(self, config, azure_sdk_provider=None):
        self.config = config

        self.client_id = config["AZURE_CLIENT_ID"]
        self.secret_key = config["AZURE_SECRET_KEY"]
        self.tenant_id = config["AZURE_TENANT_ID"]

        if azure_sdk_provider is None:
            self.sdk = AzureSDKProvider()
        else:
            self.sdk = azure_sdk_provider

    def create_environment(
        self, auth_credentials: Dict, user: User, environment: Environment
    ):
        credentials = self._get_credential_obj(self._root_creds)
        sub_client = self.sdk.subscription.SubscriptionClient(credentials)

        display_name = f"{environment.application.name}_{environment.name}_{environment.id}"  # proposed format

        billing_profile_id = "?"  # something chained from environment?
        sku_id = AZURE_SKU_ID
        # we want to set AT-AT as an owner here
        # we could potentially associate subscriptions with "management groups" per DOD component
        body = self.sdk.subscription.models.ModernSubscriptionCreationParameters(
            display_name,
            billing_profile_id,
            sku_id,
            # owner=<AdPrincipal: for AT-AT user>
        )

        # These 2 seem like something that might be worthwhile to allow tiebacks to
        # TOs filed for the environment
        billing_account_name = "?"
        invoice_section_name = "?"
        # We may also want to create billing sections in the enrollment account
        sub_creation_operation = sub_client.subscription_factory.create_subscription(
            billing_account_name, invoice_section_name, body
        )

        # the resulting object from this process is a link to the new subscription
        # not a subscription model, so we'll have to unpack the ID
        new_sub = sub_creation_operation.result()

        subscription_id = self._extract_subscription_id(new_sub.subscription_link)
        if subscription_id:
            return subscription_id
        else:
            # troublesome error, subscription should exist at this point
            # but we just don't have a valid ID
            pass

    def create_atat_admin_user(
        self, auth_credentials: Dict, csp_environment_id: str
    ) -> Dict:
        root_creds = self._root_creds
        credentials = self._get_credential_obj(root_creds)

        sub_client = self.sdk.subscription.SubscriptionClient(credentials)
        subscription = sub_client.subscriptions.get(csp_environment_id)

        managment_principal = self._get_management_service_principal()

        auth_client = self.sdk.authorization.AuthorizationManagementClient(
            credentials,
            # TODO: Determine which subscription this needs to point at
            # Once we're in a multi-sub environment
            subscription.id,
        )

        # Create role assignment for
        role_assignment_id = str(uuid4())
        role_assignment_create_params = auth_client.role_assignments.models.RoleAssignmentCreateParameters(
            role_definition_id=REMOTE_ROOT_ROLE_DEF_ID,
            principal_id=managment_principal.id,
        )

        auth_client.role_assignments.create(
            scope=f"/subscriptions/{subscription.id}/",
            role_assignment_name=role_assignment_id,
            parameters=role_assignment_create_params,
        )

        return {
            "csp_user_id": managment_principal.object_id,
            "credentials": managment_principal.password_credentials,
            "role_name": role_assignment_id,
        }

    def create_tenant(self, payload):
        # auth as SP that is allowed to create tenant? (tenant creation sp creds)
        # create tenant with owner details (populated from portfolio point of contact, pw is generated)

        # return tenant id, tenant owner id and tenant owner object id from:
        response = {"tenantId": "string", "userId": "string", "objectId": "string"}
        return self._ok(
            {
                "tenant_id": response["tenantId"],
                "user_id": response["userId"],
                "user_object_id": response["objectId"],
            }
        )

    def create_billing_owner(self, creds, tenant_admin_details):
        # authenticate as tenant_admin
        # create billing owner identity

        # TODO: Lookup response format
        # Managed service identity?
        response = {"id": "string"}
        return self._ok({"billing_owner_id": response["id"]})

    def assign_billing_owner(self, creds, billing_owner_id, tenant_id):
        # TODO: Do we source role definition ID from config, api or self-defined?
        # TODO: If from api,
        """
        {
            "principalId": "string",
            "principalTenantId": "string",
            "billingRoleDefinitionId": "string"
        }
        """

        return self.ok()

    def create_billing_profile(self, creds, tenant_admin_details, billing_owner_id):
        # call billing profile creation endpoint, specifying owner
        # Payload:
        """
        {
            "displayName": "string",
            "poNumber": "string",
            "address": {
                "firstName": "string",
                "lastName": "string",
                "companyName": "string",
                "addressLine1": "string",
                "addressLine2": "string",
                "addressLine3": "string",
                "city": "string",
                "region": "string",
                "country": "string",
                "postalCode": "string"
            },
            "invoiceEmailOptIn": true,
            Note: These last 2 are also the body for adding/updating new TOs/clins
            "enabledAzurePlans": [
                {
                "skuId": "string"
                }
            ],
            "clinBudget": {
                "amount": 0,
                "startDate": "2019-12-18T16:47:40.909Z",
                "endDate": "2019-12-18T16:47:40.909Z",
                "externalReferenceId": "string"
            }
        }
        """

        # response will be mostly the same as the body, but we only really care about the id
        response = {"id": "string"}
        return self._ok({"billing_profile_id": response["id"]})

    def report_clin(self, creds, clin_id, clin_amount, clin_start, clin_end, clin_to):
        # should consumer be responsible for reporting each clin or
        # should this take a list and manage the sequential reporting?
        """ Payload
        {
            "enabledAzurePlans": [
                {
                "skuId": "string"
                }
            ],
            "clinBudget": {
                "amount": 0,
                "startDate": "2019-12-18T16:47:40.909Z",
                "endDate": "2019-12-18T16:47:40.909Z",
                "externalReferenceId": "string"
            }
        }
        """

        # we don't need any of the returned info for this
        return self._ok()

    def create_remote_admin(self, creds, tenant_details):
        # create app/service principal within tenant, with name constructed from tenant details
        # assign principal global admin

        # needs to call out to CLI with tenant owner username/password, prototyping for that underway

        # return identifier and creds to consumer for storage
        response = {"clientId": "string", "secretKey": "string", "tenantId": "string"}
        return self._ok(
            {
                "client_id": response["clientId"],
                "secret_key": response["secret_key"],
                "tenant_id": response["tenantId"],
            }
        )

    def force_tenant_admin_pw_update(self, creds, tenant_owner_id):
        # use creds to update to force password recovery?
        # not sure what the endpoint/method for this is, yet

        return self._ok()

    def create_billing_alerts(self, TBD):
        # TODO: Add azure-mgmt-consumption for Budget and Notification entities/operations
        # TODO: Determine how to auth against that API using the SDK, doesn't seeem possible at the moment
        # TODO: billing alerts are registered as Notifications on Budget objects, which have start/end dates
        # TODO: determine what the keys in the Notifications dict are supposed to be
        # we may need to rotate budget objects when new TOs/CLINs are reported?

        # we likely only want the budget ID, can be updated or replaced?
        response = {"id": "id"}
        return self._ok({"budget_id": response["id"]})

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

    def _extract_subscription_id(self, subscription_url):
        sub_id_match = SUBSCRIPTION_ID_REGEX.match(subscription_url)

        if sub_id_match:
            return sub_id_match.group(1)

    def _get_credential_obj(self, creds, resource=None):

        return self.sdk.credentials.ServicePrincipalCredentials(
            client_id=creds.get("client_id"),
            secret=creds.get("secret_key"),
            tenant=creds.get("tenant_id"),
            resource=resource,
            cloud_environment=self.sdk.cloud,
        )

    def _make_tenant_admin_cred_obj(self, username, password):
        return self.sdk.credentials.UserPassCredentials(username, password)

    def _ok(self, body=None):
        return self._make_response("ok", body)

    def _error(self, body=None):
        return self._make_response("error", body)

    def _make_response(self, status, body=dict()):
        """Create body for responses from API

        Arguments:
            status {string} -- "ok" or "error"
            body {dict} -- dict containing details of response or error, if applicable

        Returns:
            dict -- status of call with body containing details
        """
        return {"status": status, "body": body}

    @property
    def _root_creds(self):
        return {
            "client_id": self.client_id,
            "secret_key": self.secret_key,
            "tenant_id": self.tenant_id,
        }
