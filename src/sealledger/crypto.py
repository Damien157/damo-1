import hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization
from typing import Tuple


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def generate_ed25519_keypair() -> Tuple[bytes, bytes]:
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    priv_bytes = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return priv_bytes, pub_bytes


def sign(priv_bytes: bytes, message: bytes) -> bytes:
    priv = Ed25519PrivateKey.from_private_bytes(priv_bytes)
    return priv.sign(message)


def verify(pub_bytes: bytes, message: bytes, signature: bytes) -> bool:
    pub = Ed25519PublicKey.from_public_bytes(pub_bytes)
    try:
        pub.verify(signature, message)
        return True
    except Exception:
        return False


def merkle_root(elements: list[bytes]) -> str:
    # simple merkle: pairwise hash until single root
    if not elements:
        return sha256_hex(b"")
    curr = [hashlib.sha256(e).digest() for e in elements]
    while len(curr) > 1:
        next_level = []
        for i in range(0, len(curr), 2):
            a = curr[i]
            b = curr[i + 1] if i + 1 < len(curr) else a
            next_level.append(hashlib.sha256(a + b).digest())
        curr = next_level
    return curr[0].hex()


def anchor_ledger(data: bytes) -> dict:
    # prototype: produce a local timestamped anchor. Replace with RFC-3161 or on-chain anchoring in production.
    from datetime import datetime

    return {"anchor_hash": sha256_hex(data), "timestamp": datetime.utcnow().isoformat(), "method": "local-timestamp"}


def pub_from_priv(priv_bytes: bytes) -> bytes:
    priv = Ed25519PrivateKey.from_private_bytes(priv_bytes)
    pub = priv.public_key()
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return pub_bytes
