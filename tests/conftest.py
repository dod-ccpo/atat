import os
from collections import OrderedDict
from logging.config import dictConfig
from unittest.mock import Mock

import pendulum
import pytest
from werkzeug.datastructures import FileStorage

import alembic.command
import alembic.config
import tests.factories as factories
from atat.app import make_app, make_config
from atat.database import db as _db
from tests.mocks import PDF_FILENAME, PDF_FILENAME2
from tests.utils import FakeLogger, FakeNotificationSender

dictConfig({"version": 1, "handlers": {"wsgi": {"class": "logging.NullHandler"}}})

pytest_plugins = ("celery.contrib.pytest",)


def pytest_addoption(parser):
    parser.addoption("--hybrid", action="store_true", default=False)
    parser.addoption("--subscriptions", action="store_true", default=False)
    parser.addoption(
        "--repeat", action="store", help="Number of times to repeat each test"
    )


def pytest_generate_tests(metafunc):
    if metafunc.config.option.repeat is not None:
        count = int(metafunc.config.option.repeat)

        # Append fixture that accepts how many times each test should be repeated
        metafunc.fixturenames.append("tmp_ct")
        metafunc.parametrize("tmp_ct", range(count))


def set_skip_mark_for_option(option, config, items):
    if config.getoption(f"--{option}"):
        return
    skip_option_mark = pytest.mark.skip(reason=f"need --{option} option to run")
    for item in items:
        if option in item.keywords:
            item.add_marker(skip_option_mark)


def pytest_collection_modifyitems(config, items):
    set_skip_mark_for_option("hybrid", config, items)
    set_skip_mark_for_option("subscriptions", config, items)


@pytest.fixture(scope="session")
def app(request):
    config = make_config()
    _app = make_app(config)

    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(autouse=True)
def skip_audit_log(request):
    """
    Conditionally skip tests marked with 'audit_log' based on the
    USE_AUDIT_LOG config value.
    """
    config = make_config()
    if request.node.get_closest_marker("audit_log"):
        use_audit_log = config.get("USE_AUDIT_LOG", False)
        if not use_audit_log:
            pytest.skip("audit log feature flag disabled")


@pytest.fixture(scope="function")
def no_debug_app(request):
    config = make_config(direct_config={"default": {"DEBUG": False}})
    _app = make_app(config)

    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope="function")
def no_debug_client(no_debug_app):
    yield no_debug_app.test_client()


def apply_migrations():
    """Applies all alembic migrations."""
    alembic_config = os.path.join(os.path.dirname(__file__), "../", "alembic.ini")
    config = alembic.config.Config(alembic_config)
    app_config = make_config()
    config.set_main_option("sqlalchemy.url", app_config["DATABASE_URI"])
    alembic.command.upgrade(config, "head")


@pytest.fixture(scope="session")
def db(app, request):

    _db.app = app

    apply_migrations()

    yield _db

    _db.drop_all()


def determine_session_scope(fixture_name, config):
    if config.getoption("--hybrid", None):
        return "session"
    else:
        return "function"


@pytest.fixture(scope=determine_session_scope, autouse=True)
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    factory_list = [
        cls
        for _name, cls in factories.__dict__.items()
        if isinstance(cls, type) and cls.__module__ == "tests.factories"
    ]
    for factory in factory_list:
        factory._meta.sqlalchemy_session = session
        factory._meta.sqlalchemy_session_persistence = "commit"

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


class DummyForm(dict):
    def __init__(self, data=OrderedDict(), errors=(), raw_data=None):
        self._fields = data
        self.errors = list(errors)


class DummyField(object):
    def __init__(self, data=None, errors=(), raw_data=None, name=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data
        self.name = name


@pytest.fixture
def dummy_form():
    return DummyForm()


@pytest.fixture
def dummy_field():
    return DummyField()


@pytest.fixture
def user_session(monkeypatch, session):
    def set_user_session(user=None):
        monkeypatch.setattr(
            "atat.domain.auth.get_current_user",
            lambda *args: user or factories.UserFactory.create(),
        )

    return set_user_session


@pytest.fixture
def pdf_upload():
    with open(PDF_FILENAME, "rb") as fp:
        yield FileStorage(fp, content_type="application/pdf")


@pytest.fixture
def pdf_upload2():
    with open(PDF_FILENAME2, "rb") as fp:
        yield FileStorage(fp, content_type="application/pdf")


@pytest.fixture
def downloaded_task_order():
    with open(PDF_FILENAME, "rb") as fp:
        yield {"name": "mock.pdf", "content": fp.read()}


@pytest.fixture
def mock_logger(app):
    real_logger = app.logger
    app.logger = FakeLogger()

    yield app.logger

    app.logger = real_logger


@pytest.fixture(scope="function", autouse=True)
def notification_sender(app):
    real_notification_sender = app.notification_sender
    app.notification_sender = FakeNotificationSender()

    yield app.notification_sender

    app.notification_sender = real_notification_sender


# This is the only effective means I could find to disable logging. Setting a
# `celery_enable_logging` fixture to return False should work according to the
# docs, but doesn't:
# https://docs.celeryproject.org/en/latest/userguide/testing.html#celery-enable-logging-override-to-enable-logging-in-embedded-workers
@pytest.fixture(scope="function")
def celery_worker_parameters():
    return {"loglevel": "FATAL"}
