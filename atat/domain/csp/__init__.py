import os

from .cloud import MockCloudProvider, HybridCloudProvider, AzureCloudProvider
from .files import AzureFileService, MockFileService
from .reports import MockReportingProvider


class MockCSP:
    def __init__(self, app, simulate_failures=False):
        self.cloud = MockCloudProvider(
            app.config,
            with_delay=simulate_failures,
            with_failure=simulate_failures,
            with_authorization=simulate_failures,
        )
        self.files = MockFileService(app)
        self.reports = MockReportingProvider()


class AzureCSP:
    def __init__(self, app):
        self.cloud = MockCloudProvider(app.config)
        self.files = AzureFileService(app.config)
        self.reports = MockReportingProvider()


class HybridCSP:
    def __init__(self, app, simulate_failures=False):
        azure = AzureCloudProvider(app.config)
        mock = MockCloudProvider(
            app.config,
            with_delay=simulate_failures,
            with_failure=simulate_failures,
            with_authorization=simulate_failures,
        )
        self.cloud = HybridCloudProvider(azure, mock, app.config)
        self.files = AzureFileService(app.config)
        self.reports = MockReportingProvider()


def make_csp_provider(app, csp=None):
    simulate_failures = app.config.get("SIMULATE_API_FAILURE")
    app.logger.info(f"Created a cloud service provider in '{csp}' mode!")
    if csp == "azure":
        app.csp = AzureCSP(app)
    elif csp == "mock-test":
        app.csp = MockCSP(app, simulate_failures=simulate_failures)
    elif csp == "hybrid":
        app.csp = HybridCSP(app, simulate_failures=simulate_failures)
    else:
        app.csp = MockCSP(app)
