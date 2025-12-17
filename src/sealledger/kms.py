import os
from typing import Tuple
from .crypto import generate_ed25519_keypair, sign, verify, sha256_hex


class KMSInterface:
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        raise NotImplementedError()

    def sign(self, key_ref: bytes, message: bytes) -> bytes:
        raise NotImplementedError()

    def verify(self, key_ref: bytes, message: bytes, signature: bytes) -> bool:
        raise NotImplementedError()


class LocalKMS(KMSInterface):
    """Local KMS shim for development: stores a single keypair in project 'keys/' directory."""

    def __init__(self, key_dir: str | None = None):
        self.key_dir = key_dir or os.getenv("SEALLEDGER_KEY_DIR", "./keys")
        os.makedirs(self.key_dir, exist_ok=True)
        self.priv_path = os.path.join(self.key_dir, "ed25519_priv.bin")
        self.pub_path = os.path.join(self.key_dir, "ed25519_pub.bin")
        if not (os.path.exists(self.priv_path) and os.path.exists(self.pub_path)):
            priv, pub = generate_ed25519_keypair()
            with open(self.priv_path, "wb") as f:
                f.write(priv)
            with open(self.pub_path, "wb") as f:
                f.write(pub)

    def load_keys(self) -> Tuple[bytes, bytes]:
        with open(self.priv_path, "rb") as f:
            priv = f.read()
        with open(self.pub_path, "rb") as f:
            pub = f.read()
        return priv, pub

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        return self.load_keys()

    def sign(self, key_ref: bytes | None, message: bytes) -> bytes:
        # ignore key_ref; we only have one key
        priv, _ = self.load_keys()
        return sign(priv, message)

    def verify(self, key_ref: bytes | None, message: bytes, signature: bytes) -> bool:
        _, pub = self.load_keys()
        return verify(pub, message, signature)


class AWSKMS(KMSInterface):
    def __init__(self, key_id: str):
        self.key_id = key_id
        import boto3
        # Allow overriding endpoint for localstack in tests via AWS_KMS_ENDPOINT
        self.endpoint_url = os.getenv("AWS_KMS_ENDPOINT")
        self.client = boto3.client("kms", endpoint_url=self.endpoint_url)

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        # AWS KMS stores keys; we can't export private key. Return key_id as public reference.
        return (self.key_id.encode(), b"")

    def sign(self, key_ref: bytes | None, message: bytes) -> bytes:
        # key_ref is optional; fallback to configured key_id
        kid = key_ref.decode() if isinstance(key_ref, (bytes, bytearray)) else self.key_id
        resp = self.client.sign(KeyId=kid, Message=message, MessageType="RAW", SigningAlgorithm="ECDSA_SHA_256")
        return resp["Signature"]

    def verify(self, key_ref: bytes | None, message: bytes, signature: bytes) -> bool:
        kid = key_ref.decode() if isinstance(key_ref, (bytes, bytearray)) else self.key_id
        resp = self.client.verify(KeyId=kid, Message=message, Signature=signature, MessageType="RAW", SigningAlgorithm="ECDSA_SHA_256")
        return bool(resp.get("SignatureValid", False))
