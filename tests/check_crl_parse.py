import os
import pytest

from atat.domain.authnid.crl.util import crl_local_path, CRL_LIST

from tests.utils import parse_for_issuer_and_next_update


CRL_DIR = "crls"


@pytest.mark.parametrize("crl_uri, issuer", CRL_LIST)
def test_crl_scan_against_parse(crl_uri, issuer):
    crl_path = crl_local_path(CRL_DIR, crl_uri)
    parsed_der = parse_for_issuer_and_next_update(crl_path)
    assert issuer == parsed_der.hex()
