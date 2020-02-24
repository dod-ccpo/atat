from atat.domain.exceptions import UnauthenticatedError, NotFoundError
from atat.domain.users import Users
from .utils import parse_sdn, email_from_certificate
from .crl import CRLRevocationException, CRLInvalidException


class AuthenticationContext:
    def __init__(self, crl_cache, auth_status, sdn, cert):
        if None in locals().values():
            raise UnauthenticatedError(
                "Missing required authentication context components"
            )

        self.crl_cache = crl_cache
        self.auth_status = auth_status
        self.sdn = sdn
        self.cert = cert.encode()
        self._parsed_sdn = None

    def authenticate(self):
        if not self.auth_status == "SUCCESS":
            raise UnauthenticatedError("SSL/TLS client authentication failed")

        self._crl_check()

        return True

    def get_user(self):
        try:
            return Users.get_by_dod_id(self.parsed_sdn["dod_id"])

        except NotFoundError:
            email = self._get_user_email()
            return Users.create(permission_sets=[], email=email, **self.parsed_sdn)

    def _get_user_email(self):
        try:
            return email_from_certificate(self.cert)

        # this just means it is not an email certificate; we might choose to
        # log in that case
        except ValueError:
            return None

    def _crl_check(self):
        try:
            self.crl_cache.crl_check(self.cert)
        except CRLRevocationException as exc:
            raise UnauthenticatedError("CRL check failed. " + str(exc))

    @property
    def parsed_sdn(self):
        if not self._parsed_sdn:
            try:
                self._parsed_sdn = parse_sdn(self.sdn)
            except ValueError as exc:
                raise UnauthenticatedError(str(exc))

        return self._parsed_sdn
