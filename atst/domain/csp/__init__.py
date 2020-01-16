import importlib

from .cloud import MockCloudProvider
from .file_uploads import AzureUploader, MockUploader
from .reports import MockReportingProvider


class MockCSP:
    def __init__(self, app, test_mode=False):
        self.cloud = MockCloudProvider(
            app.config,
            with_delay=(not test_mode),
            with_failure=(not test_mode),
            with_authorization=(not test_mode),
        )
        self.files = MockUploader(app)
        self.reports = MockReportingProvider()


class AzureCSP:
    def __init__(self, app):
        self.cloud = MockCloudProvider(app.config)
        self.files = AzureUploader(app.config)
        self.reports = MockReportingProvider()


def make_csp_provider(app, csp=None):
    if csp == "azure":
        app.csp = AzureCSP(app)
    elif csp == "mock-test":
        app.csp = MockCSP(app, test_mode=True)
    else:
        app.csp = MockCSP(app)


def _stage_to_classname(stage):
    return "".join(
        map(lambda word: word.capitalize(), stage.replace("_", " ").split(" "))
    )


def get_stage_csp_class(stage, class_type):
    """
    given a stage name and class_type return the class
    class_type is either 'payload' or 'result'

    """
    cls_name = "".join([_stage_to_classname(stage), "CSP", class_type.capitalize()])
    try:
        return getattr(importlib.import_module("atst.domain.csp.cloud"), cls_name)
    except AttributeError:
        print("could not import CSP Result class <%s>" % cls_name)
