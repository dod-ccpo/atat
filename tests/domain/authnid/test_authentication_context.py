import pytest

from atst.domain.authnid import AuthenticationContext
from atst.domain.exceptions import UnauthenticatedError, NotFoundError
from atst.domain.users import Users

from tests.mocks import DOD_SDN_INFO, DOD_SDN, FIXTURE_EMAIL_ADDRESS
from tests.factories import UserFactory

CERT = open("tests/fixtures/{}.crt".format(FIXTURE_EMAIL_ADDRESS)).read()


class MockCRLCache():
    def get_store(self, cert):
        pass


def test_can_authenticate(monkeypatch):
    monkeypatch.setattr("atst.domain.authnid.Validator.validate", lambda s: True)
    auth_context = AuthenticationContext(
        MockCRLCache(), "SUCCESS", DOD_SDN, CERT
    )
    assert auth_context.authenticate()


def test_unsuccessful_status(monkeypatch):
    monkeypatch.setattr("atst.domain.authnid.Validator.validate", lambda s: True)
    auth_context = AuthenticationContext(
        MockCRLCache(), "FAILURE", DOD_SDN, CERT
    )
    with pytest.raises(UnauthenticatedError) as excinfo:
        assert auth_context.authenticate()

    (message,) = excinfo.value.args
    assert "client authentication" in message


def test_crl_check_fails(monkeypatch):
    monkeypatch.setattr("atst.domain.authnid.Validator.validate", lambda s: False)
    auth_context = AuthenticationContext(
        MockCRLCache(), "SUCCESS", DOD_SDN, CERT
    )
    with pytest.raises(UnauthenticatedError) as excinfo:
        assert auth_context.authenticate()

    (message,) = excinfo.value.args
    assert "CRL check" in message


def test_bad_sdn(monkeypatch):
    monkeypatch.setattr("atst.domain.authnid.Validator.validate", lambda s: True)
    auth_context = AuthenticationContext(
        MockCRLCache(), "SUCCESS", "abc123", CERT
    )
    with pytest.raises(UnauthenticatedError) as excinfo:
        auth_context.get_user()

    (message,) = excinfo.value.args
    assert "SDN" in message


def test_user_exists(monkeypatch):
    monkeypatch.setattr("atst.domain.authnid.Validator.validate", lambda s: True)
    user = UserFactory.create(**DOD_SDN_INFO)
    auth_context = AuthenticationContext(
        MockCRLCache(), "SUCCESS", DOD_SDN, CERT
    )
    auth_user = auth_context.get_user()

    assert auth_user == user


def test_creates_user(monkeypatch):
    monkeypatch.setattr("atst.domain.authnid.Validator.validate", lambda s: True)
    # check user does not exist
    with pytest.raises(NotFoundError):
        Users.get_by_dod_id(DOD_SDN_INFO["dod_id"])

    auth_context = AuthenticationContext(
        MockCRLCache(), "SUCCESS", DOD_SDN, CERT
    )
    user = auth_context.get_user()
    assert user.dod_id == DOD_SDN_INFO["dod_id"]
    assert user.email == FIXTURE_EMAIL_ADDRESS


def test_user_cert_has_no_email(monkeypatch):
    monkeypatch.setattr("atst.domain.authnid.Validator.validate", lambda s: True)
    cert = open("ssl/client-certs/atat.mil.crt").read()
    auth_context = AuthenticationContext(
        MockCRLCache(), "SUCCESS", DOD_SDN, cert
    )
    user = auth_context.get_user()

    assert user.email == None
