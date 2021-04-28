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
    """A general problem with the connection, timeouts or unresolved endpoints"""

    def __init__(self, connection_error):
        self.connection_error = connection_error

    @property
    def message(self):
        return "Could not connect to cloud provider: {}".format(self.connection_error)


class UnknownServerException(GeneralCSPException):
    """An error occured on the CSP side (5xx) and we don't know why"""

    def __init__(self, status_code, server_error):
        self.status_code = status_code
        self.server_error = server_error

    @property
    def message(self):
        return f"A server error with status code [{self.status_code}] occured: {self.server_error}"


class EnvironmentCreationException(GeneralCSPException):
    """If there was an error in creating the environment"""

    def __init__(self, env_identifier, reason):
        self.env_identifier = env_identifier
        self.reason = reason

    @property
    def message(self):
        return "The envionment {} couldn't be created: {}".format(
            self.env_identifier, self.reason
        )


class ResourceProvisioningError(GeneralCSPException):
    """Failed to provision a cloud-specific resource"""

    def __init__(self, resource, reason):
        self.resource = resource
        self.reason = reason

    @property
    def message(self):
        return f"Failed to provision {self.resource}: {self.reason}"


class UserProvisioningException(GeneralCSPException):
    """Failed to provision a user"""


class UserRemovalException(GeneralCSPException):
    """Failed to remove a user"""

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


class DomainNameException(GeneralCSPException):
    """A problem occured when generating the domain name for a tenant"""

    def __init__(self, name):
        self.name = name

    @property
    def message(self):
        return f"Could not generate unique tenant name for {self.name}"
