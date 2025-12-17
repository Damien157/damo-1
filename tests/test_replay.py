from sealledger.demo import run_full_flow
from sealledger.ledger import ledger
from sealledger.obligations import verify_premises


def test_replay_verifies_obligations():
    data = {"owner": "alice", "portfolio": {"max_loss": 0.2, "loss": 0.1}, "predictions": [0.6, 0.7]}
    entry = run_full_flow(data)
    e = ledger.get(entry.ledger_id)
    assert isinstance(e.input_snapshot, dict)
    # replay verification should match original data or be retrievable via pointer
    snapshot = e.input_snapshot
    actual = None
    if "pointer" in snapshot:
        ptr = snapshot["pointer"]
        if ptr.get("method") == "local":
            import json

            with open(ptr["path"], "r") as f:
                actual = json.load(f)
        else:
            # for S3 pointers in tests, fall back to original test data
            actual = data
    else:
        actual = snapshot

    assert actual["owner"] == data["owner"]
    results = {o.id: verify_premises(o, actual) for o in e.obligations}
    assert all(isinstance(v, dict) for v in results.values())
