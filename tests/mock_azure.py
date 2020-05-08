import json
from unittest.mock import Mock

import pytest

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

KEYVAULT_SECRET = {
    **AUTH_CREDENTIALS,
    "tenant_id": "mock_tenant_id",
    "tenant_admin_username": "mock_tenant_admin_username",
    "tenant_admin_password": "mock_tenant_admin_password",
}

MOCK_ACCESS_TOKEN = "TOKEN"


def mock_managementgroups():
    from azure.mgmt import managementgroups

    return Mock(spec=managementgroups)


def mock_credentials():
    import azure.common.credentials as credentials

    return Mock(spec=credentials)


def mock_identity():
    import azure.identity as identity

    return Mock(spec=identity)


def mock_azure_exceptions():
    from azure.core import exceptions

    return exceptions


def mock_cloud_details():
    from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD

    return AZURE_PUBLIC_CLOUD


def mock_adal():
    import adal
    from adal.adal_error import AdalError

    mock_adal = Mock(spec=adal)
    mock_adal.AdalError = AdalError
    mock_adal.AuthenticationContext.return_value.acquire_token_with_client_credentials.return_value = {
        "accessToken": MOCK_ACCESS_TOKEN
    }
    mock_adal.AuthenticationContext.return_value.acquire_token_with_username_password.return_value = {
        "accessToken": MOCK_ACCESS_TOKEN
    }
    return mock_adal


def mock_requests():
    import requests

    mock_requests = Mock(wraps=requests)
    mock_requests.exceptions = requests.exceptions
    return mock_requests


class MockAzureSDK(object):
    def __init__(self):

        self.managementgroups = mock_managementgroups()
        self.credentials = mock_credentials()
        self.identity = mock_identity()
        self.azure_exceptions = mock_azure_exceptions()
        self.cloud = mock_cloud_details()
        self.adal = mock_adal()
        self.requests = mock_requests()


@pytest.fixture(scope="function")
def mock_azure(monkeypatch):
    monkeypatch.setattr(
        AzureCloudProvider,
        "_get_elevated_management_token",
        Mock(return_value=MOCK_ACCESS_TOKEN),
    )
    monkeypatch.setattr(
        AzureCloudProvider, "validate_domain_name", Mock(return_value=True),
    )
    azure_cloud_provider = AzureCloudProvider(
        AZURE_CONFIG, azure_sdk_provider=MockAzureSDK()
    )
    monkeypatch.setattr(
        azure_cloud_provider,
        "get_secret",
        Mock(return_value=json.dumps(KEYVAULT_SECRET)),
    )
    monkeypatch.setattr(azure_cloud_provider, "set_secret", Mock(return_value=None))
    monkeypatch.setattr(
        azure_cloud_provider, "_get_keyvault_token", Mock(return_value="TOKEN")
    )
    return azure_cloud_provider
