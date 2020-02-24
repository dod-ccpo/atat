import os
import re
import hashlib
import logging

from OpenSSL import crypto, SSL
from flask import current_app as app

from .util import load_crl_locations_cache, serialize_crl_locations_cache, CRL_LIST

# error codes from OpenSSL: https://github.com/openssl/openssl/blob/2c75f03b39de2fa7d006bc0f0d7c58235a54d9bb/include/openssl/x509_vfy.h#L111
CRL_EXPIRED_ERROR_CODE = 12


def get_common_name(x509_name_object):
    for comp in x509_name_object.get_components():
        if comp[0] == b"CN":
            return comp[1].decode()


class CRLRevocationException(Exception):
    pass


class CRLInvalidException(Exception):
    # CRL expired
    # CRL missing
    pass


class CRLInterface:
    def __init__(self, *args, logger=None, **kwargs):
        self.logger = logger

    def _log(self, message, level=logging.INFO):
        if self.logger:
            self.logger.log(level, message, extra={"tags": ["authorization", "crl"]})

    def crl_check(self, cert):
        raise NotImplementedError()


class NoOpCRLCache(CRLInterface):
    def _get_cn(self, cert):
        try:
            parsed = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
            return get_common_name(parsed.get_subject())
        except crypto.Error:
            pass

        return "unknown"

    def crl_check(self, cert):
        cn = self._get_cn(cert)
        self._log(
            "Did not perform CRL validation for certificate with Common Name '{}'".format(
                cn
            )
        )

        return True


class CRLCache(CRLInterface):

    _PEM_RE = re.compile(
        b"-----BEGIN CERTIFICATE-----\r?.+?\r?-----END CERTIFICATE-----\r?\n?",
        re.DOTALL,
    )

    def __init__(
        self,
        root_location,
        crl_dir,
        store_class=crypto.X509Store,
        logger=None,
        crl_list=CRL_LIST,
    ):
        self._crl_dir = crl_dir
        self.logger = logger
        self.store_class = store_class
        self.certificate_authorities = {}
        self.crl_list = crl_list
        self._load_roots(root_location)
        self._build_crl_cache()

    def _get_store(self, cert):
        return self._build_store(cert.get_issuer())

    def _load_roots(self, root_location):
        with open(root_location, "rb") as f:
            for raw_ca in self._parse_roots(f.read()):
                ca = crypto.load_certificate(crypto.FILETYPE_PEM, raw_ca)
                self.certificate_authorities[ca.get_subject().der()] = ca

    def _parse_roots(self, root_str):
        return [match.group(0) for match in self._PEM_RE.finditer(root_str)]

    def _build_crl_cache(self):
        try:
            self.crl_cache = load_crl_locations_cache(self._crl_dir)
        except FileNotFoundError:
            self.crl_cache = serialize_crl_locations_cache(
                self._crl_dir, crl_list=self.crl_list
            )

    def _load_crl(self, crl_location):
        with open(crl_location, "rb") as crl_file:
            try:
                return crypto.load_crl(crypto.FILETYPE_ASN1, crl_file.read())
            except crypto.Error:
                self._log(
                    "Could not load CRL at location {}".format(crl_location),
                    level=logging.WARNING,
                )

    def _build_store(self, issuer):
        store = self.store_class()
        self._log("STORE ID: {}. Building store.".format(id(store)))
        store.set_flags(crypto.X509StoreFlags.CRL_CHECK)
        crl_location = self.crl_cache.get(issuer.der())
        issuer_name = get_common_name(issuer)

        if not crl_location:
            raise CRLInvalidException(
                "Could not find matching CRL for issuer with Common Name {}".format(
                    issuer_name
                )
            )

        crl = self._load_crl(crl_location)
        store.add_crl(crl)

        self._log(
            "STORE ID: {}. Adding CRL with issuer Common Name {}".format(
                id(store), issuer_name
            )
        )

        store = self._add_certificate_chain_to_store(store, crl.get_issuer())
        return store

    # this _should_ happen just twice for the DoD PKI (intermediary, root) but
    # theoretically it can build a longer certificate chain

    def _add_certificate_chain_to_store(self, store, issuer):
        ca = self.certificate_authorities.get(issuer.der())
        store.add_cert(ca)
        self._log(
            "STORE ID: {}. Adding CA with subject {}".format(
                id(store), ca.get_subject()
            )
        )

        if issuer == ca.get_issuer():
            # i.e., it is the root CA and we are at the end of the chain
            return store

        else:
            return self._add_certificate_chain_to_store(store, ca.get_issuer())

    def crl_check(self, cert):
        parsed = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        store = self._get_store(parsed)
        context = crypto.X509StoreContext(store, parsed)
        try:
            context.verify_certificate()
            return True

        except crypto.X509StoreContextError as err:
            if err.args[0][0] == CRL_EXPIRED_ERROR_CODE:
                if app.config.get("CRL_FAIL_OPEN"):
                    self._log(
                        "Encountered expired CRL for certificate with CN {} and issuer CN {}, failing open.".format(
                            parsed.get_subject().CN, parsed.get_issuer().CN
                        ),
                        level=logging.WARNING,
                    )
                    return True
                else:
                    raise CRLInvalidException("CRL expired. Args: {}".format(err.args))
            raise CRLRevocationException(
                "Certificate revoked or errored. Error: {}. Args: {}".format(
                    type(err), err.args
                )
            )
