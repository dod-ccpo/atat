import re

import cryptography.x509 as x509
from cryptography.hazmat.backends import default_backend


def parse_sdn(sdn):
    try:
        parts = sdn.split(",")
        cn_string = [piece for piece in parts if re.match("^CN=", piece)][0]
        cn = cn_string.split("=")[-1]
        info = cn.split(".")
        return {"last_name": info[0], "first_name": info[1], "dod_id": info[-1]}

    except (IndexError, AttributeError):
        raise ValueError("'{}' is not a valid SDN".format(sdn))


def email_from_certificate(cert_file):
    cert = x509.load_pem_x509_certificate(cert_file, default_backend())
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        email = ext.value.get_values_for_type(x509.RFC822Name)
        if email:
            return email[0]

        else:
            raise ValueError(
                "No email available for certificate with serial {}".format(
                    cert.serial_number
                )
            )

    except x509.extensions.ExtensionNotFound:
        raise ValueError(
            "No subjectAltName available for certificate with serial {}".format(
                cert.serial_number
            )
        )
