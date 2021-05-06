from atat.utils.environment import (
    ApplicationEnvironment,
    get_application_environment_name,
)


def test_get_application_environment_name():
    assert (
        get_application_environment_name("blue")
        is ApplicationEnvironment.PRODUCTION.value
    ), "If the name of the environment is not registered, would return production"
    assert (
        get_application_environment_name(ApplicationEnvironment.DEVELOPMENT.value)
        is ApplicationEnvironment.DEVELOPMENT.value
    ), "development is a valid name for the environment"
    assert (
        get_application_environment_name(ApplicationEnvironment.TEST.value)
        is ApplicationEnvironment.TEST.value
    ), "test is a valid name for the environment"
    assert (
        get_application_environment_name(ApplicationEnvironment.CI.value)
        is ApplicationEnvironment.CI.value
    ), "ci is a valid name for the environment"
