import pytest
from unittest.mock import Mock

from atat.domain.csp.cloud import AzureCloudProvider

AZURE_CONFIG = {
    "AZURE_CALC_CLIENT_ID": "MOCK",
    "AZURE_CALC_SECRET": "MOCK",  # pragma: allowlist secret
    "AZURE_CALC_RESOURCE": "http://calc",
    "AZURE_CLIENT_ID": "MOCK",
    "AZURE_SECRET_KEY": "MOCK",
    "AZURE_TENANT_ID": "MOCK",
    "AZURE_POLICY_LOCATION": "policies",
    "AZURE_VAULT_URL": "http://vault",
    "AZURE_POWERSHELL_CLIENT_ID": "MOCK",
    "AZURE_ROLE_DEF_ID_OWNER": "MOCK",
    "AZURE_ROLE_DEF_ID_CONTRIBUTOR": "MOCK",
    "AZURE_ROLE_DEF_ID_BILLING_READER": "MOCK",
    "AZURE_GRAPH_RESOURCE": "MOCK",
    "AZURE_AADP_QTY": 5,
}

AUTH_CREDENTIALS = {
    "client_id": AZURE_CONFIG["AZURE_CLIENT_ID"],
    "secret_key": AZURE_CONFIG["AZURE_SECRET_KEY"],
    "tenant_id": AZURE_CONFIG["AZURE_TENANT_ID"],
}


def mock_subscription():
    from azure.mgmt import subscription

    return Mock(spec=subscription)


def mock_authorization():
    from azure.mgmt import authorization

    return Mock(spec=authorization)


def mock_managementgroups():
    from azure.mgmt import managementgroups

    return Mock(spec=managementgroups)


def mock_graphrbac():
    import azure.graphrbac as graphrbac

    return Mock(spec=graphrbac)


def mock_credentials():
    import azure.common.credentials as credentials

    return Mock(spec=credentials)


def mock_identity():
    import azure.identity as identity

    return Mock(spec=identity)


def mock_policy():
    from azure.mgmt.resource import policy

    return Mock(spec=policy)


def mock_azure_exceptions():
    from azure.core import exceptions

    return exceptions


def mock_adal():
    import adal

    return Mock(spec=adal)


def mock_requests():
    import requests

    mock_requests = Mock(wraps=requests)
    mock_requests.exceptions = requests.exceptions
    return mock_requests


def mock_secrets():
    from azure.keyvault import secrets

    return Mock(spec=secrets)


def mock_cloud_details():
    from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD

    return AZURE_PUBLIC_CLOUD


class MockAzureSDK(object):
    def __init__(self):

        self.subscription = mock_subscription()
        self.authorization = mock_authorization()
        self.policy = mock_policy()
        self.adal = mock_adal()
        self.managementgroups = mock_managementgroups()
        self.graphrbac = mock_graphrbac()
        self.credentials = mock_credentials()
        self.identity = mock_identity()
        self.azure_exceptions = mock_azure_exceptions()
        self.policy = mock_policy()
        self.secrets = mock_secrets()
        self.requests = mock_requests()
        self.cloud = mock_cloud_details()
        self.identity = mock_identity()


@pytest.fixture(scope="function")
def mock_azure():
    return AzureCloudProvider(AZURE_CONFIG, azure_sdk_provider=MockAzureSDK())
