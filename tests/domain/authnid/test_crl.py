# Import installed packages
import pytest
import re
import os
import shutil
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding
from OpenSSL import crypto

from atat.domain.authnid.crl import (
    CRLCache,
    CRLRevocationException,
    CRLInvalidException,
    NoOpCRLCache,
)
from atat.domain.authnid.crl.util import (
    load_crl_locations_cache,
    serialize_crl_locations_cache,
    CRLParseError,
    JSON_CACHE,
)

from tests.mocks import FIXTURE_EMAIL_ADDRESS, DOD_CN
from tests.utils import FakeLogger, parse_for_issuer_and_next_update, make_crl_list


class MockX509Store:
    def __init__(self):
        self.crls = []
        self.certs = []

    def add_crl(self, crl):
        self.crls.append(crl)

    def add_cert(self, cert):
        self.certs.append(cert)

    def set_flags(self, flag):
        pass


def test_can_build_crl_list(crl_file, ca_key, ca_file, make_crl, tmpdir):
    crl = make_crl(ca_key)
    issuer_der = crl.issuer.public_bytes(default_backend())
    dir_ = os.path.dirname(crl_file)
    serialize_crl_locations_cache(dir_, crl_list=[(str(crl_file), issuer_der.hex())])
    cache = CRLCache(ca_file, dir_, store_class=MockX509Store)
    assert len(cache.crl_cache.keys()) == 1
    assert issuer_der in cache.crl_cache
    assert cache.crl_cache[issuer_der] == crl_file


def test_can_build_trusted_root_list(app):
    location = "ssl/server-certs/ca-chain.pem"
    cache = CRLCache(
        location, app.config["CRL_STORAGE_CONTAINER"], store_class=MockX509Store
    )
    with open(location) as f:
        content = f.read()
        assert len(cache.certificate_authorities.keys()) == content.count("BEGIN CERT")


def test_crl_validation_on_login(
    app,
    client,
    ca_key,
    ca_file,
    crl_file,
    rsa_key,
    make_x509,
    make_crl,
    serialize_pki_object_to_disk,
):
    good_cert = make_x509(rsa_key(), signer_key=ca_key, cn="luke")
    bad_cert = make_x509(rsa_key(), signer_key=ca_key, cn="darth")

    crl = make_crl(ca_key, expired_serials=[bad_cert.serial_number])
    serialize_pki_object_to_disk(crl, crl_file, encoding=Encoding.DER)
    crl_dir = os.path.dirname(crl_file)

    crl_list = make_crl_list(good_cert, crl_file)
    cache = CRLCache(ca_file, crl_dir, crl_list=crl_list)
    assert cache.crl_check(good_cert.public_bytes(Encoding.PEM).decode())
    with pytest.raises(CRLRevocationException):
        cache.crl_check(bad_cert.public_bytes(Encoding.PEM).decode())


def test_can_dynamically_update_crls(
    ca_key,
    ca_file,
    crl_file,
    rsa_key,
    make_x509,
    make_crl,
    serialize_pki_object_to_disk,
):
    crl_dir = os.path.dirname(crl_file)
    client_cert = make_x509(rsa_key(), signer_key=ca_key, cn="chewbacca")
    client_pem = client_cert.public_bytes(Encoding.PEM)
    crl_list = make_crl_list(client_cert, crl_file)
    cache = CRLCache(ca_file, crl_dir, crl_list=crl_list)
    assert cache.crl_check(client_pem)

    revoked_crl = make_crl(ca_key, expired_serials=[client_cert.serial_number])
    # override the original CRL with one that revokes client_cert
    serialize_pki_object_to_disk(revoked_crl, crl_file, encoding=Encoding.DER)

    with pytest.raises(CRLRevocationException):
        assert cache.crl_check(client_pem)


def test_throws_error_for_missing_issuer(app):
    cache = CRLCache(
        "ssl/server-certs/ca-chain.pem", app.config["CRL_STORAGE_CONTAINER"]
    )
    # this cert is self-signed, and so the application does not have a
    # corresponding CRL for it
    cert = open("tests/fixtures/{}.crt".format(FIXTURE_EMAIL_ADDRESS), "rb").read()
    with pytest.raises(CRLInvalidException) as exc:
        assert cache.crl_check(cert)
    (message,) = exc.value.args
    # objects that the issuer is missing
    assert "issuer" in message
    # names the issuer we were expecting to find a CRL for; same as the
    # certificate subject in this case because the cert is self-signed
    assert DOD_CN in message


FIXTURE_CRL_CACHE = "tests/fixtures/chain/crl_locations.json"


def setup_function(test_multistep_certificate_chain):
    if os.path.isfile(FIXTURE_CRL_CACHE):
        os.remove(FIXTURE_CRL_CACHE)


def test_multistep_certificate_chain():
    issuer = None
    fixture_crl = "tests/fixtures/chain/intermediate.crl"
    with open(fixture_crl, "rb") as crl_file:
        crl = crypto.load_crl(crypto.FILETYPE_ASN1, crl_file.read())
        issuer = crl.get_issuer().der()

    crl_list = [(fixture_crl, issuer.hex())]
    cache = CRLCache(
        "tests/fixtures/chain/ca-chain.pem", "tests/fixtures/chain/", crl_list=crl_list
    )
    cert = open("tests/fixtures/chain/client.crt", "rb").read()
    assert cache.crl_check(cert)


def test_no_op_crl_cache_logs_common_name():
    logger = FakeLogger()
    cert = open("ssl/client-certs/atat.mil.crt", "rb").read()
    cache = NoOpCRLCache(logger=logger)
    assert cache.crl_check(cert)
    assert "ART.GARFUNKEL.1234567890" in logger.messages[-1]


def test_expired_crl_raises_CRLInvalidException_with_failover_config_false(
    app, ca_file, expired_crl_file, ca_key, make_x509, rsa_key
):
    client_cert = make_x509(rsa_key(), signer_key=ca_key, cn="chewbacca")
    client_pem = client_cert.public_bytes(Encoding.PEM)
    crl_dir = os.path.dirname(expired_crl_file)
    crl_list = make_crl_list(client_cert, expired_crl_file)
    crl_cache = CRLCache(ca_file, crl_dir, crl_list=crl_list)
    with pytest.raises(CRLInvalidException):
        crl_cache.crl_check(client_pem)


def test_expired_crl_passes_with_failover_config_true(
    ca_file, expired_crl_file, ca_key, make_x509, rsa_key, crl_failover_open_app
):
    client_cert = make_x509(rsa_key(), signer_key=ca_key, cn="chewbacca")
    client_pem = client_cert.public_bytes(Encoding.PEM)
    crl_dir = os.path.dirname(expired_crl_file)
    crl_list = make_crl_list(client_cert, expired_crl_file)
    crl_cache = CRLCache(ca_file, crl_dir, crl_list=crl_list)

    assert crl_cache.crl_check(client_pem)


def test_load_crl_locations_cache(crl_file):
    dir_ = os.path.dirname(crl_file)
    serialize_crl_locations_cache(dir_)
    cache = load_crl_locations_cache(dir_)
    assert isinstance(cache, dict)
