import os
from sealledger.timestamp import LocalTimestamp, RFC3161Timestamp, get_provider


def test_local_timestamp_anchor():
    lt = LocalTimestamp()
    a = lt.anchor(b"payload")
    assert "anchor_hash" in a and a["method"] == "local-timestamp"


def test_get_provider_default():
    os.environ.pop("TIMESTAMP_PROVIDER", None)
    p = get_provider()
    assert isinstance(p, LocalTimestamp)


def test_rfc3161_raises_without_url():
    os.environ["TIMESTAMP_PROVIDER"] = "rfc3161"
    os.environ.pop("TSA_URL", None)
    try:
        p = get_provider()
        assert False, "expected runtime error"
    except RuntimeError:
        pass
