import os
from datetime import datetime
from typing import Protocol
from .crypto import sha256_hex


class TimestampProvider(Protocol):
    def anchor(self, data: bytes) -> dict:
        ...


class LocalTimestamp:
    """Local timestamp provider for development/testing."""

    def anchor(self, data: bytes) -> dict:
        return {"anchor_hash": sha256_hex(data), "timestamp": datetime.utcnow().isoformat(), "method": "local-timestamp"}


class RFC3161Timestamp:
    """RFC-3161 TSA client. Requires env var TSA_URL. Uses rfc3161ng library."""

    def __init__(self, tsa_url: str | None = None):
        self.tsa_url = tsa_url or os.getenv("TSA_URL")
        if not self.tsa_url:
            raise RuntimeError("TSA_URL must be set for RFC3161Timestamp")

    def anchor(self, data: bytes) -> dict:
        # perform TSA request and return token hex + tsa time
        # Use rfc3161ng helpers to construct a proper TSQ
        from rfc3161ng import make_timestamp_request, encode_timestamp_request
        import requests

        req = make_timestamp_request(data=data, hashname="sha256")
        body = encode_timestamp_request(req)
        headers = {"Content-Type": "application/timestamp-query"}
        resp = requests.post(self.tsa_url, data=body, headers=headers)
        resp.raise_for_status()
        token = resp.content.hex()
        return {"anchor_token": token, "method": "rfc3161", "tsa_url": self.tsa_url}


def get_provider() -> TimestampProvider:
    prov = os.getenv("TIMESTAMP_PROVIDER", "local")
    if prov == "rfc3161":
        return RFC3161Timestamp()
    return LocalTimestamp()
