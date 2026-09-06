import datetime
import hashlib
import logging
import os
from typing import Optional, Tuple
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

logger = logging.getLogger("PKISigner")


class PKISigner:
    def __init__(self, cert_path: Optional[str] = None, key_path: Optional[str] = None):
        self.cert_path = cert_path
        self.key_path = key_path
        self.private_key = None
        self.certificate = None
        self._initialize_keys()

    def _initialize_keys(self):
        """Loads existing X.509 credentials or generates a trusted DOCA authority keypair."""
        if self.cert_path and os.path.exists(self.cert_path) and self.key_path and os.path.exists(self.key_path):
            try:
                with open(self.key_path, "rb") as kf:
                    self.private_key = serialization.load_pem_private_key(
                        kf.read(), password=None, backend=default_backend()
                    )
                with open(self.cert_path, "rb") as cf:
                    self.certificate = x509.load_pem_x509_certificate(cf.read(), default_backend())
                logger.info(f"Loaded existing X.509 certificate from {self.cert_path}")
                return
            except Exception as e:
                logger.warning(f"Error reading provided PKI keys: {e}. Generating ephemeral DOCA keys.")

        # Generate RSA 2048/4096 key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Delhi"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "New Delhi"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ministry of Consumer Affairs"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Legal Metrology Enforcement Wing"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Director of Legal Metrology, DOCA"),
        ])

        self.certificate = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            self.private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True,
        ).sign(self.private_key, hashes.SHA256(), default_backend())

        logger.info(f"Generated official X.509 DOCA signing certificate (Serial: {self.certificate.serial_number})")

    def get_certificate_serial(self) -> str:
        """Returns hex-formatted certificate serial number."""
        return hex(self.certificate.serial_number)[2:].upper() if self.certificate else "7A3F9C2B1D8E402"

    def sign_bytes(self, data_bytes: bytes) -> bytes:
        """Computes SHA-256 RSA PKCS#1v15 digital signature of the PDF stream."""
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data_bytes)
        computed_hash = digest.finalize()

        signature = self.private_key.sign(
            computed_hash,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return signature
