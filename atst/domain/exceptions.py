class NotFoundError(Exception):
    def __init__(self, resource_name):
        self.resource_name = resource_name

    @property
    def message(self):
        return "No {} could be found.".format(self.resource_name)


class AlreadyExistsError(Exception):
    def __init__(self, resource_name):
        self.resource_name = resource_name

    @property
    def message(self):
        return "{} already exists".format(self.resource_name)
