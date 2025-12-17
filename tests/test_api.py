from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_api_flow_and_replay():
    data = {"owner": "alice", "portfolio": {"max_loss": 0.2, "loss": 0.1}, "predictions": [0.6, 0.7]}
    # ingest
    r = client.post("/ingest", json={"data": data})
    assert r.status_code == 200
    obligations = r.json()["obligations"]
    assert isinstance(obligations, list)

    # bond first obligation
    oid = obligations[0]["id"]
    r2 = client.post(f"/bond/{oid}", json={"data": data})
    assert r2.status_code == 200

    # stitch
    sigs = {"s1": {"source": "src", "payload": {"k": 1}}}
    r3 = client.post("/stitch", json={"signals": sigs})
    comp = r3.json()["composite"]

    # seal ledger
    r4 = client.post("/seal-ledger", json={"obligations": obligations, "composite": comp, "robustness": {"seal_strength": 1.0, "gate_efficacy": 1.0, "composite_robustness": 1.0, "confidence": 1.0}, "seals": {"sig": "00"}, "input_snapshot": data})
    assert r4.status_code == 200
    lid = r4.json()["ledger_id"]

    # replay
    r5 = client.get(f"/ledger/{lid}/replay")
    assert r5.status_code == 200
    j = r5.json()
    assert "verifications" in j


def test_api_persistent_ledger(monkeypatch, tmp_path):
    # enable persistent ledger and set sqlite file for tests
    db_path = tmp_path / "test_api.db"
    monkeypatch.setenv("PERSISTENT_LEDGER", "1")
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{db_path}")
    # reload repository to pick up env var
    from importlib import reload
    import sealledger.repository as repo

    reload(repo)
    # run the flow
    data = {"owner": "alice", "portfolio": {"max_loss": 0.2, "loss": 0.1}, "predictions": [0.6, 0.7]}
    r = client.post("/ingest", json={"data": data})
    obligations = r.json()["obligations"]
    comp = client.post("/stitch", json={"signals": {"s1": {"source": "src", "payload": {"k": 1}}}}).json()["composite"]
    r4 = client.post("/seal-ledger", json={"ledger_id": "L-001", "obligations": obligations, "composite": comp, "robustness": {"seal_strength": 1.0, "gate_efficacy": 1.0, "composite_robustness": 1.0, "confidence": 1.0}, "seals": {"sig": "00"}, "input_snapshot": data})
    assert r4.status_code == 200
    # ensure DB contains the ledger
    from sealledger.repository import get_ledger, init_db
    init_db()
    g = get_ledger("L-001")
    assert g is not None
