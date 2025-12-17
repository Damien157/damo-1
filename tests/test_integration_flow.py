from sealledger.demo import run_full_flow


def test_integration_full_flow():
    data = {"owner": "alice", "portfolio": {"max_loss": 0.2, "loss": 0.1}, "predictions": [0.6, 0.7]}
    entry = run_full_flow(data)
    assert entry.ledger_id is not None
    assert len(entry.obligations) >= 1
