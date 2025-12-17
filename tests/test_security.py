from sealledger.crypto import anchor_ledger


def test_anchor_ledger():
    data = b"ledger payload"
    a = anchor_ledger(data)
    assert "anchor_hash" in a and "timestamp" in a
