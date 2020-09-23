import json
from unittest.mock import Mock

import pytest

import atat.domain.csp.cloud.azure_cloud_provider
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

KEYVAULT_SECRET = {
    "root_sp_client_id": AZURE_CONFIG["AZURE_CLIENT_ID"],
    "root_sp_key": AZURE_CONFIG["AZURE_SECRET_KEY"],
    "root_tenant_id": AZURE_CONFIG["AZURE_TENANT_ID"],
    "tenant_id": "mock_tenant_id",
    "tenant_admin_username": "mock_tenant_admin_username",
    "tenant_admin_password": "mock_tenant_admin_password",  # pragma: allowlist secret
    "tenant_sp_client_id": AZURE_CONFIG["AZURE_CLIENT_ID"],
    "tenant_sp_key": AZURE_CONFIG["AZURE_SECRET_KEY"],
}

MOCK_ACCESS_TOKEN = "TOKEN"


def mock_cloud_details():
    from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD

    return AZURE_PUBLIC_CLOUD


def mock_requests():
    import requests

    mock_requests = Mock(wraps=requests)
    mock_requests.exceptions = requests.exceptions
    return mock_requests


class MockAzureSDK(object):
    def __init__(self):
        self.cloud = mock_cloud_details()
        self.requests = mock_requests()


@pytest.fixture(scope="function")
def mock_azure(monkeypatch):
    monkeypatch.setattr(
        atat.domain.csp.cloud.azure_cloud_provider,
        "get_principal_auth_token",
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
        "_elevate_tenant_admin_access",
        Mock(return_value=MOCK_ACCESS_TOKEN),
    )
    monkeypatch.setattr(
        azure_cloud_provider,
        "get_secret",
        Mock(return_value=json.dumps(KEYVAULT_SECRET)),
    )
    monkeypatch.setattr(azure_cloud_provider, "set_secret", Mock(return_value=None))
    monkeypatch.setattr(
        azure_cloud_provider,
        "_get_keyvault_token",
        Mock(return_value=MOCK_ACCESS_TOKEN),
    )
    return azure_cloud_provider
