class NotFoundError(Exception):
    def __init__(self, resource_name, resource_id=None):
        self.resource_name = resource_name
        self.resource_id = resource_id

    @property
    def message(self):
        return "No {} could be found.".format(self.resource_name)


class AlreadyExistsError(Exception):
    def __init__(self, resource_name):
        self.resource_name = resource_name

    @property
    def message(self):
        return "{} already exists".format(self.resource_name)


class UnauthorizedError(Exception):
    def __init__(self, user, action):
        self.user = user
        self.action = action

    @property
    def message(self):
        return "User {} not authorized to {}".format(self.user.id, self.action)


class UnauthenticatedError(Exception):
    @property
    def message(self):
        return str(self)


class UploadError(Exception):
    pass


class NoAccessError(Exception):
    def __init__(self, resource_name):
        self.resource_name = resource_name

    @property
    def message(self):
        return "Route for {} cannot be accessed".format(self.resource_name)


class ClaimFailedException(Exception):
    def __init__(self, resource):
        self.resource = resource
        message = (
            f"Could not acquire claim for {resource.__class__.__name__} {resource.id}."
        )
        super().__init__(message)


class DisabledError(Exception):
    def __init__(self, resource_name, resource_id=None):
        self.resource_name = resource_name
        self.resource_id = resource_id

    @property
    def message(self):
        return f"Cannot update disabled {self.resource_name} {self.resource_id}."
