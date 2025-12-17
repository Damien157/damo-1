import os
from typing import Tuple
from .crypto import generate_ed25519_keypair, sign, verify, sha256_hex

try:
    from google.cloud import kms_v1  # type: ignore
    from google.protobuf import duration_pb2  # noqa: F401
except Exception:  # pragma: no cover - optional dep
    kms_v1 = None


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


class GCPKMS(KMSInterface):
    """GCP KMS adapter using google-cloud-kms.

    Notes:
    - Assumes an asymmetric signing key is created in KMS and the key resource
      name (projects/.../keyRings/.../cryptoKeys/.../cryptoKeyVersions/...) is provided.
    - `sign` calls `asymmetric_sign` and returns raw signature bytes.
    - `verify` fetches the public key via `get_public_key` and verifies locally.
    """

    def __init__(self, key_name: str):
        if kms_v1 is None:
            raise RuntimeError("google-cloud-kms is not installed")
        self.key_name = key_name
        # Allow overriding endpoint for emulator via GCP_KMS_ENDPOINT
        endpoint = os.getenv("GCP_KMS_ENDPOINT")
        if endpoint:
            client_options = {"api_endpoint": endpoint}
            self.client = kms_v1.KeyManagementServiceClient(client_options=client_options)
        else:
            self.client = kms_v1.KeyManagementServiceClient()

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        # Can't export private key; return key resource name (as bytes) as a reference
        return (self.key_name.encode(), b"")

    def sign(self, key_ref: bytes | None, message: bytes) -> bytes:
        name = key_ref.decode() if isinstance(key_ref, (bytes, bytearray)) else self.key_name
        request = {"name": name, "digest": {"sha256": __import__("hashlib").sha256(message).digest()}}
        resp = self.client.asymmetric_sign(request=request)
        return resp.signature

    def verify(self, key_ref: bytes | None, message: bytes, signature: bytes) -> bool:
        # Fetch public key and verify locally using cryptography
        name = key_ref.decode() if isinstance(key_ref, (bytes, bytearray)) else self.key_name
        resp = self.client.get_public_key(request={"name": name})
        pem = resp.pem
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        try:
            pub = load_pem_public_key(pem.encode())
            digest = __import__("hashlib").sha256(message).digest()
            pub.verify(signature, digest, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False
