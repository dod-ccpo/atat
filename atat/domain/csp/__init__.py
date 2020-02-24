from .cloud import MockCloudProvider
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


def make_csp_provider(app, csp=None):
    if csp == "azure":
        app.csp = AzureCSP(app)
    elif csp == "mock-test":
        app.csp = MockCSP(app, test_mode=True)
    else:
        app.csp = MockCSP(app)
