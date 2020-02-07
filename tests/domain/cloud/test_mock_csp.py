import pytest

from atst.domain.csp import MockCloudProvider
from atst.domain.csp.cloud.models import EnvironmentCSPPayload, EnvironmentCSPResult

from tests.factories import EnvironmentFactory, EnvironmentRoleFactory, UserFactory

CREDENTIALS = MockCloudProvider(config={})._auth_credentials


@pytest.fixture
def mock_csp():
    return MockCloudProvider(config={}, with_delay=False, with_failure=False)


def test_create_environment(mock_csp: MockCloudProvider):
    environment = EnvironmentFactory.create()
    environment.application.cloud_id = "parent_id"
    environment.application.portfolio.csp_data = {"tenant_id": "fake"}
    payload = EnvironmentCSPPayload(
        **dict(
            tenant_id=environment.application.portfolio.csp_data.get("tenant_id"),
            display_name=environment.name,
            parent_id=environment.application.cloud_id,
        )
    )
    result = mock_csp.create_environment(payload)
    assert isinstance(result, EnvironmentCSPResult)


def test_create_or_update_user(mock_csp: MockCloudProvider):
    env_role = EnvironmentRoleFactory.create()
    csp_user_id = mock_csp.create_or_update_user(CREDENTIALS, env_role, "csp_role_id")
    assert isinstance(csp_user_id, str)


def test_disable_user(mock_csp: MockCloudProvider):
    assert mock_csp.disable_user(CREDENTIALS, "csp_user_id")
