import pytest
from sqlalchemy.orm import sessionmaker, scoped_session

from atst.app import make_app, make_deps, make_config
from atst.database import make_db
from tests.mocks import MockApiClient, MockFundzClient, MockRequestsClient, MockAuthzClient
from atst.sessions import DictSessions


@pytest.fixture
def app(db):
    TEST_DEPS = {
        "authz_client": MockAuthzClient("authz"),
        "requests_client": MockRequestsClient("requests"),
        "authnid_client": MockApiClient("authnid"),
        "fundz_client": MockFundzClient("fundz"),
        "sessions": DictSessions(),
        "db_session": db
    }

    config = make_config()
    deps = make_deps(config)
    deps.update(TEST_DEPS)

    return make_app(config, deps)


@pytest.fixture(scope='function')
def db():

    # Override db with a new SQLAlchemy session so that we can rollback
    # each test's transaction.
    # Inspiration: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#session-external-transaction
    config = make_config()
    database = make_db(config)
    connection = database.get_bind().connect()
    transaction = connection.begin()
    db = scoped_session(sessionmaker(bind=connection))

    yield db

    db.close()
    transaction.rollback()
    connection.close()


class DummyForm(dict):
    pass


class DummyField(object):
    def __init__(self, data=None, errors=(), raw_data=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data


@pytest.fixture
def dummy_form():
    return DummyForm()


@pytest.fixture
def dummy_field():
    return DummyField()
