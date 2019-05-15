import os
import pytest
import alembic.config
import alembic.command
from logging.config import dictConfig
from werkzeug.datastructures import FileStorage
from tempfile import TemporaryDirectory
from collections import OrderedDict

from atst.app import make_app, make_config
from atst.database import db as _db
from atst.queue import queue as atst_queue
import tests.factories as factories
from tests.mocks import PDF_FILENAME, PDF_FILENAME2
from tests.utils import FakeLogger, FakeNotificationSender

from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID


dictConfig({"version": 1, "handlers": {"wsgi": {"class": "logging.NullHandler"}}})


@pytest.fixture(scope="session")
def app(request):
    upload_dir = TemporaryDirectory()

    config = make_config()
    config.update(
        {"STORAGE_CONTAINER": upload_dir.name, "CRL_STORAGE_PROVIDER": "LOCAL"}
    )

    _app = make_app(config)

    ctx = _app.app_context()
    ctx.push()

    yield _app

    upload_dir.cleanup()

    ctx.pop()


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


@pytest.fixture(scope="function", autouse=True)
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
            "atst.domain.auth.get_current_user",
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
def extended_financial_verification_data(pdf_upload):
    return {
        "funding_type": "RDTE",
        "funding_type_other": "other",
        "expiration_date": "1/1/{}".format(datetime.date.today().year + 1),
        "clin_0001": "50000",
        "clin_0003": "13000",
        "clin_1001": "30000",
        "clin_1003": "7000",
        "clin_2001": "30000",
        "clin_2003": "7000",
        "legacy_task_order": pdf_upload,
    }


@pytest.fixture(scope="function", autouse=True)
def queue():
    yield atst_queue
    atst_queue.get_queue().empty()


@pytest.fixture
def crl_failover_open_app(app):
    app.config.update({"CRL_FAIL_OPEN": True})
    yield app
    app.config.update({"CRL_FAIL_OPEN": False})


@pytest.fixture
def rsa_key():
    def _rsa_key():
        return rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

    return _rsa_key


@pytest.fixture
def ca_key(rsa_key):
    return rsa_key()


@pytest.fixture
def make_x509():
    def _make_x509(private_key, signer_key=None, cn="ATAT", signer_cn="ATAT"):
        if signer_key is None:
            signer_key = private_key

        one_day = timedelta(1, 0, 0)
        public_key = private_key.public_key()
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
        )
        builder = builder.issuer_name(
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, signer_cn)])
        )
        if signer_key == private_key:
            builder = builder.add_extension(
                x509.BasicConstraints(ca=True, path_length=None), critical=True
            )
        builder = builder.not_valid_before(datetime.today() - (one_day * 2))
        builder = builder.not_valid_after(datetime.today() + (one_day * 30))
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.public_key(public_key)
        certificate = builder.sign(
            private_key=signer_key, algorithm=hashes.SHA256(), backend=default_backend()
        )

        return certificate

    return _make_x509


@pytest.fixture
def make_crl():
    def _make_crl(
        private_key,
        last_update_days=-1,
        next_update_days=30,
        cn="ATAT",
        expired_serials=None,
    ):
        one_day = timedelta(1, 0, 0)
        builder = x509.CertificateRevocationListBuilder()
        builder = builder.issuer_name(
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
        )
        last_update = datetime.today() + (one_day * last_update_days)
        next_update = datetime.today() + (one_day * next_update_days)
        builder = builder.last_update(last_update)
        builder = builder.next_update(next_update)
        if expired_serials:
            for serial in expired_serials:
                builder = add_revoked_cert(builder, serial, last_update)

        crl = builder.sign(
            private_key=private_key,
            algorithm=hashes.SHA256(),
            backend=default_backend(),
        )

        return crl

    return _make_crl


def add_revoked_cert(crl_builder, serial, revocation_date):
    revoked_cert = (
        x509.RevokedCertificateBuilder()
        .serial_number(serial)
        .revocation_date(revocation_date)
        .build(default_backend())
    )
    return crl_builder.add_revoked_certificate(revoked_cert)


@pytest.fixture
def serialize_pki_object_to_disk():
    def _serialize_pki_object_to_disk(obj, name, encoding=Encoding.PEM):
        with open(name, "wb") as file_:
            file_.write(obj.public_bytes(encoding))

            return name

    return _serialize_pki_object_to_disk


@pytest.fixture
def ca_file(make_x509, ca_key, tmpdir, serialize_pki_object_to_disk):
    ca = make_x509(ca_key)
    ca_out = tmpdir.join("atat-ca.crt")
    serialize_pki_object_to_disk(ca, ca_out)

    return ca_out


@pytest.fixture
def expired_crl_file(make_crl, ca_key, tmpdir, serialize_pki_object_to_disk):
    crl = make_crl(ca_key, last_update_days=-7, next_update_days=-1)
    crl_out = tmpdir.join("atat-expired.crl")
    serialize_pki_object_to_disk(crl, crl_out, encoding=Encoding.DER)

    return crl_out


@pytest.fixture
def crl_file(make_crl, ca_key, tmpdir, serialize_pki_object_to_disk):
    crl = make_crl(ca_key)
    crl_out = tmpdir.join("atat-valid.crl")
    serialize_pki_object_to_disk(crl, crl_out, encoding=Encoding.DER)

    return crl_out


@pytest.fixture
def mock_logger(app):
    real_logger = app.logger
    app.logger = FakeLogger()

    yield app.logger

    app.logger = real_logger


@pytest.fixture
def notification_sender(app):
    real_notification_sender = app.notification_sender
    app.notification_sender = FakeNotificationSender()

    yield app.notification_sender

    app.notification_sender = real_notification_sender
