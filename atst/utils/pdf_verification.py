import hashlib
from OpenSSL import crypto
from asn1crypto import cms, pem, core
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


class PDFSignature:
    def __init__(self, byte_range_start=None, crl_check=None, pdf=None):
        self._signers_cert = None
        self._openssl_loaded_certificate = None
        self.byte_range_start = byte_range_start
        self.crl_check = crl_check
        self.pdf = pdf

    @property
    def byte_range(self):
        """
        This returns an array of 4 numbers that represent the byte range of
        the PDF binary file that is signed by the certificate.

        E.G: [0, 2045, 3012, 5012]

        Bytes    0 to 2045 - represent part A of the signed file
        Bytes 2046 to 3012 - would contain the signature and certificate information
        Bytes 3013 to 5012 - represent part B of the signed file
        """
        start = self.pdf.find(b"[", self.byte_range_start)
        stop = self.pdf.find(b"]", start)
        contents_range = [int(i, 10) for i in self.pdf[start + 1 : stop].split()]

        return contents_range

    @property
    def signed_binary_data(self):
        """
        This is the binary data stored in the signature
        """
        br = self.byte_range
        contents = self.pdf[br[0] + br[1] + 1 : br[2] - 1]
        data = []

        for i in range(0, len(contents), 2):
            data.append(int(contents[i : i + 2], 16))

        return cms.ContentInfo.load(bytes(data))["content"]

    @property
    def signers_cert(self):
        """
        This returns the certificate used to sign the PDF
        """
        if self._signers_cert is None:
            for cert in self.signed_binary_data["certificates"]:
                if (
                    self.signers_serial
                    == cert.native["tbs_certificate"]["serial_number"]
                ):
                    cert = cert.dump()
                    self._signers_cert = pem.armor("CERTIFICATE", cert)
                    break

        return self._signers_cert

    @property
    def signers_serial(self):
        """
        Return the signers serial from their certificate
        """
        return self.signed_binary_data["signer_infos"][0]["sid"].native["serial_number"]

    @property
    def hashing_algorithm(self):
        """
        This is the hashing algorithm used to generate the hash of binary file content
        which is then signed by the certificate.

        E.G. sha256, sha1
        """
        return self.signed_binary_data["digest_algorithms"][0]["algorithm"].native

    @property
    def openssl_loaded_certificate(self):
        if self._openssl_loaded_certificate is None:
            self._openssl_loaded_certificate = crypto.load_certificate(
                crypto.FILETYPE_PEM, self.signers_cert
            )
        return self._openssl_loaded_certificate

    @property
    def cert_common_name(self):
        """
        This returns the common name on the certificate. This might be a name or
        a DOD ID for example.
        """
        return self.openssl_loaded_certificate.get_subject().commonName

    @property
    def encrypted_hash_of_signed_document(self):
        """
        This is the calculated hash of the PDF binary data stored in the
        signature. We calculate it outselves and then compare to this
        so we can see if data has changed.
        """
        stored_hash = None

        for attr in self.signed_binary_data["signer_infos"][0]["signed_attrs"]:
            if attr["type"].native == "message_digest":
                stored_hash = attr["values"].native[0]
                break

        return stored_hash

    @property
    def binary_data(self):
        """
        Take the byte range and return the binary data for that rage.
        """
        br = self.byte_range
        data1 = self.pdf[br[0] : br[0] + br[1]]
        data2 = self.pdf[br[2] : br[2] + br[3]]

        return data1 + data2

    @property
    def hashed_binary_data(self):
        """
        Takes the data in the byte range and hashes it using
        the hashing algorithm specified in the signed PDF. We
        can later compare this to the encrypted_hash_of_signed_document.
        """
        return getattr(hashlib, self.hashing_algorithm)(self.binary_data)

    @property
    def is_cert_valid(self):
        """
        Takes the signing certificate and runs it through the CRLCache
        checker. Returns a boolean.
        """
        return self.crl_check(self.signers_cert)

    @property
    def is_signature_valid(self):
        """
        Get signed PDF signature and determine if it was actually signed
        by the certificate that it claims it was. Returns a boolean.
        """
        public_key = self.openssl_loaded_certificate.get_pubkey().to_cryptography_key()
        attrs = self.signed_binary_data["signer_infos"][0]["signed_attrs"]
        signed_data = None

        if attrs is not None and not isinstance(attrs, core.Void):
            signed_data = attrs.dump()
            signed_data = b"\x31" + signed_data[1:]
        else:
            signed_data = self.binary_data

        try:
            public_key.verify(
                bytes(self.signed_binary_data["signer_infos"][0]["signature"]),
                signed_data,
                padding.PKCS1v15(),
                getattr(hashes, self.hashing_algorithm.upper())(),
            )
            return True
        except Exception:
            return False

    @property
    def to_dict(self):
        is_cert_valid = self.is_cert_valid
        is_signature_valid = self.is_signature_valid
        is_hash_valid = (
            self.hashed_binary_data.digest() == self.encrypted_hash_of_signed_document
        )

        return {
            "cert_common_name": self.cert_common_name,
            "hashed_binary_data": self.hashed_binary_data.hexdigest(),
            "hashing_algorithm": self.hashing_algorithm,
            "is_valid": is_cert_valid and is_hash_valid and is_signature_valid,
            "is_valid_cert": is_cert_valid,
            "is_valid_hash": is_hash_valid,
            "is_valid_signature": is_signature_valid,
            "signers_serial": self.signers_serial,
        }


def pdf_signature_validations(pdf=None, crl_check=None):
    """
    As arguments we accept a pdf binary blob and a callable crl_check.
    An example implementation of the crl_check can be found in the
    tests (test/utils/test_pdf_verification.py)
    """
    signatures = []
    start_byte = 0

    while True:
        start = start_byte + 1
        n = pdf.find(b"/ByteRange", start)

        if n == -1:
            break

        signatures.append(
            PDFSignature(byte_range_start=n, crl_check=crl_check, pdf=pdf)
        )
        start_byte = n

    response = {"result": True, "signature_count": len(signatures), "signatures": []}

    for signature in signatures:
        sig = signature.to_dict
        response["signatures"].append(sig)

        if not sig["is_valid"]:
            response["result"] = False

    if len(signatures) == 0:
        response["result"] = False

    return response
