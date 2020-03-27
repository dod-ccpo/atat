import os

from .cloud import MockCloudProvider, HybridCloudProvider, AzureCloudProvider
from .files import AzureFileService, MockFileService
from .reports import MockReportingProvider


class MockCSP:
    def __init__(self, app, test_mode=False):
        self.cloud = MockCloudProvider(
            app.config,
            with_delay=(not test_mode),
            with_failure=(not test_mode),
            with_authorization=(not test_mode),
        )
        self.files = MockFileService(app)
        self.reports = MockReportingProvider()


class AzureCSP:
    def __init__(self, app):
        self.cloud = MockCloudProvider(app.config)
        self.files = AzureFileService(app.config)
        self.reports = MockReportingProvider()


class HybridCSP:
    def __init__(self, app, test_mode=False):
        app.config.update(
            {
                "AZURE_CLIENT_ID": os.environ.get("AZURE_CLIENT_ID"),
                "AZURE_SECRET_KEY": os.environ.get("AZURE_SECRET_KEY"),
                "AZURE_TENANT_ID": os.environ.get("AZURE_TENANT_ID"),
                "AZURE_VAULT_URL": os.environ.get("AZURE_VAULT_URL"),
                "AZURE_POWERSHELL_CLIENT_ID": os.environ.get(
                    "AZURE_POWERSHELL_CLIENT_ID"
                ),
            }
        )
        azure = AzureCloudProvider(app.config)
        mock = MockCloudProvider(
            app.config,
            with_delay=(not test_mode),
            with_failure=(not test_mode),
            with_authorization=(not test_mode),
        )
        self.cloud = HybridCloudProvider(azure, mock)
        self.files = MockFileService(app)
        self.reports = MockReportingProvider()


def make_csp_provider(app, csp=None):
    if csp == "azure":
        app.csp = AzureCSP(app)
    elif csp == "mock-test":
        app.csp = MockCSP(app, test_mode=True)
    elif csp == "hybrid":
        app.csp = HybridCSP(app, test_mode=True)
    else:
        app.csp = MockCSP(app)
