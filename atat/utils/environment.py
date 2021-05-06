import os
from enum import Enum


class ApplicationEnvironment(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TEST = "test"
    CI = "ci"

    # return the value or default
    @classmethod
    def get_valid(cls, environment_name=None):
        try:
            return cls(environment_name)
        except ValueError:
            return cls.PRODUCTION


def get_application_environment_name(environment_name=None):
    if not environment_name:
        environment_name = os.getenv(
            "FLASK_ENV", ApplicationEnvironment.PRODUCTION.value
        )

    return ApplicationEnvironment.get_valid(environment_name).value
