# Import installed packages
import pytest
import re
import os
import shutil
from OpenSSL import crypto, SSL

from atst.domain.authnid.crl import CRLCache, CRLRevocationException, NoOpCRLCache
import atst.domain.authnid.crl.util as util

from tests.mocks import FIXTURE_EMAIL_ADDRESS, DOD_CN


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


def test_can_build_crl_list(monkeypatch):
    location = "ssl/client-certs/client-ca.der.crl"
    cache = CRLCache(
        "ssl/client-certs/client-ca.crt",
        crl_locations=[location],
        store_class=MockX509Store,
    )
    assert len(cache.crl_cache.keys()) == 1


def test_can_build_trusted_root_list():
    location = "ssl/server-certs/ca-chain.pem"
    cache = CRLCache(
        root_location=location, crl_locations=[], store_class=MockX509Store
    )
    with open(location) as f:
        content = f.read()
        assert len(cache.certificate_authorities.keys()) == content.count("BEGIN CERT")


def test_can_build_crl_list_with_missing_crls():
    location = "ssl/client-certs/client-ca.der.crl"
    cache = CRLCache(
        "ssl/client-certs/client-ca.crt",
        crl_locations=["tests/fixtures/sample.pdf"],
        store_class=MockX509Store,
    )
    assert len(cache.crl_cache.keys()) == 0


def test_can_validate_certificate():
    cache = CRLCache(
        "ssl/server-certs/ca-chain.pem",
        crl_locations=["ssl/client-certs/client-ca.der.crl"],
    )
    good_cert = open("ssl/client-certs/atat.mil.crt", "rb").read()
    bad_cert = open("ssl/client-certs/bad-atat.mil.crt", "rb").read()
    assert cache.crl_check(good_cert)
    with pytest.raises(CRLRevocationException):
        cache.crl_check(bad_cert)


def test_can_dynamically_update_crls(tmpdir):
    crl_file = tmpdir.join("test.crl")
    shutil.copyfile("ssl/client-certs/client-ca.der.crl", crl_file)
    cache = CRLCache("ssl/server-certs/ca-chain.pem", crl_locations=[crl_file])
    cert = open("ssl/client-certs/atat.mil.crt", "rb").read()
    assert cache.crl_check(cert)
    # override the original CRL with one that revokes atat.mil.crt
    shutil.copyfile("tests/fixtures/test.der.crl", crl_file)
    with pytest.raises(CRLRevocationException):
        assert cache.crl_check(cert)


def test_throws_error_for_missing_issuer():
    cache = CRLCache("ssl/server-certs/ca-chain.pem", crl_locations=[])
    # this cert is self-signed, and so the application does not have a
    # corresponding CRL for it
    cert = open("tests/fixtures/{}.crt".format(FIXTURE_EMAIL_ADDRESS), "rb").read()
    with pytest.raises(CRLRevocationException) as exc:
        assert cache.crl_check(cert)
    (message,) = exc.value.args
    # objects that the issuer is missing
    assert "issuer" in message
    # names the issuer we were expecting to find a CRL for; same as the
    # certificate subject in this case because the cert is self-signed
    assert DOD_CN in message


def test_multistep_certificate_chain():
    cache = CRLCache(
        "tests/fixtures/chain/ca-chain.pem",
        crl_locations=["tests/fixtures/chain/intermediate.crl"],
    )
    cert = open("tests/fixtures/chain/client.crt", "rb").read()
    assert cache.crl_check(cert)


def test_parse_disa_pki_list():
    with open("tests/fixtures/disa-pki.html") as disa:
        disa_html = disa.read()
        crl_list = util.crl_list_from_disa_html(disa_html)
        href_matches = re.findall("DOD(ROOT|EMAIL|ID)?CA", disa_html)
        assert len(crl_list) > 0
        assert len(crl_list) == len(href_matches)


class MockStreamingResponse:
    def __init__(self, content_chunks, code=200):
        self.content_chunks = content_chunks
        self.status_code = code

    def iter_content(self, chunk_size=0):
        return self.content_chunks

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def test_write_crl(tmpdir, monkeypatch):
    monkeypatch.setattr(
        "requests.get", lambda u, **kwargs: MockStreamingResponse([b"it worked"])
    )
    crl = "crl_1"
    assert util.write_crl(tmpdir, "random_target_dir", crl)
    assert [p.basename for p in tmpdir.listdir()] == [crl]
    assert [p.read() for p in tmpdir.listdir()] == ["it worked"]


def test_skips_crl_if_it_has_not_been_modified(tmpdir, monkeypatch):
    monkeypatch.setattr(
        "requests.get", lambda u, **kwargs: MockStreamingResponse([b"it worked"], 304)
    )
    assert not util.write_crl(tmpdir, "random_target_dir", "crl_file_name")


class FakeLogger:
    def __init__(self):
        self.messages = []

    def info(self, msg):
        self.messages.append(msg)

    def warning(self, msg):
        self.messages.append(msg)

    def error(self, msg):
        self.messages.append(msg)


def test_refresh_crls_with_error(tmpdir, monkeypatch):
    def _mock_create_connection(*args, **kwargs):
        raise TimeoutError

    fake_crl = "https://fakecrl.com/fake.crl"

    monkeypatch.setattr(
        "urllib3.util.connection.create_connection", _mock_create_connection
    )
    monkeypatch.setattr("atst.domain.authnid.crl.util.fetch_disa", lambda *args: None)
    monkeypatch.setattr(
        "atst.domain.authnid.crl.util.crl_list_from_disa_html", lambda *args: [fake_crl]
    )

    logger = FakeLogger()
    util.refresh_crls(tmpdir, tmpdir, logger)

    assert "Error downloading {}".format(fake_crl) in logger.messages[-1]


def test_no_op_crl_cache_logs_common_name():
    logger = FakeLogger()
    cert = open("ssl/client-certs/atat.mil.crt", "rb").read()
    cache = NoOpCRLCache(logger=logger)
    assert cache.crl_check(cert)
    assert "ART.GARFUNKEL.1234567890" in logger.messages[-1]
