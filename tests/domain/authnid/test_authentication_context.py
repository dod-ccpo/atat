import pytest

from atat.domain.authnid import AuthenticationContext
from atat.domain.authnid.crl import (
    CRLCache,
    CRLRevocationException,
    CRLInvalidException,
)
from atat.domain.exceptions import UnauthenticatedError, NotFoundError
from atat.domain.users import Users

from tests.mocks import DOD_SDN_INFO, DOD_SDN, FIXTURE_EMAIL_ADDRESS
from tests.factories import UserFactory

CERT = open("tests/fixtures/{}.crt".format(FIXTURE_EMAIL_ADDRESS)).read()


class MockCRLCache:
    def __init__(self, valid=True, expired=False):
        self.valid = valid
        self.expired = expired

    def crl_check(self, cert):
        if self.valid:
            return True
        elif self.expired == True:
            raise CRLInvalidException()

        raise CRLRevocationException()


def test_can_authenticate():
    auth_context = AuthenticationContext(MockCRLCache(), "SUCCESS", DOD_SDN, CERT)
    assert auth_context.authenticate()


def test_unsuccessful_status():
    auth_context = AuthenticationContext(MockCRLCache(), "FAILURE", DOD_SDN, CERT)
    with pytest.raises(UnauthenticatedError) as excinfo:
        assert auth_context.authenticate()

    (message,) = excinfo.value.args
    assert "client authentication" in message


def test_crl_check_fails():
    auth_context = AuthenticationContext(MockCRLCache(False), "SUCCESS", DOD_SDN, CERT)
    with pytest.raises(UnauthenticatedError) as excinfo:
        assert auth_context.authenticate()

    (message,) = excinfo.value.args
    assert "CRL check" in message


def test_expired_crl_check_fails():
    auth_context = AuthenticationContext(
        MockCRLCache(valid=False, expired=True), "SUCCESS", DOD_SDN, CERT
    )
    with pytest.raises(CRLInvalidException) as excinfo:
        assert auth_context.authenticate()


def test_bad_sdn():
    auth_context = AuthenticationContext(MockCRLCache(), "SUCCESS", "abc123", CERT)
    with pytest.raises(UnauthenticatedError) as excinfo:
        auth_context.get_user()

    (message,) = excinfo.value.args
    assert "SDN" in message


def test_user_exists():
    user = UserFactory.create(**DOD_SDN_INFO)
    auth_context = AuthenticationContext(MockCRLCache(), "SUCCESS", DOD_SDN, CERT)
    auth_user = auth_context.get_user()

    assert auth_user == user


def test_creates_user():
    # check user does not exist
    with pytest.raises(NotFoundError):
        Users.get_by_dod_id(DOD_SDN_INFO["dod_id"])

    auth_context = AuthenticationContext(MockCRLCache(), "SUCCESS", DOD_SDN, CERT)
    user = auth_context.get_user()
    assert user.dod_id == DOD_SDN_INFO["dod_id"]
    assert user.email == FIXTURE_EMAIL_ADDRESS


def test_user_cert_has_no_email():
    cert = open("ssl/client-certs/atat.mil.crt").read()
    auth_context = AuthenticationContext(MockCRLCache(), "SUCCESS", DOD_SDN, cert)
    user = auth_context.get_user()

    assert user.email == None
