import pytest
import atat.domain.authnid.utils as utils
from tests.mocks import DOD_SDN, FIXTURE_EMAIL_ADDRESS


def test_parse_sdn():
    parsed = utils.parse_sdn(DOD_SDN)
    assert parsed.get("first_name") == "ART"
    assert parsed.get("last_name") == "GARFUNKEL"
    assert parsed.get("dod_id") == "5892460358"


def test_parse_bad_sdn():
    with pytest.raises(ValueError):
        utils.parse_sdn("this has nothing to do with anything")
    with pytest.raises(ValueError):
        utils.parse_sdn(None)


def test_parse_email_cert():
    cert_file = open("tests/fixtures/{}.crt".format(FIXTURE_EMAIL_ADDRESS), "rb").read()
    email = utils.email_from_certificate(cert_file)
    assert email == FIXTURE_EMAIL_ADDRESS


def test_parse_cert_with_no_email():
    cert_file = open("tests/fixtures/no-email.crt", "rb").read()
    with pytest.raises(ValueError) as excinfo:
        email = utils.email_from_certificate(cert_file)
    (message,) = excinfo.value.args
    assert "email" in message


def test_parse_cert_with_no_san():
    cert_file = open("tests/fixtures/no-san.crt", "rb").read()
    with pytest.raises(ValueError) as excinfo:
        email = utils.email_from_certificate(cert_file)
    (message,) = excinfo.value.args
    assert "subjectAltName" in message
