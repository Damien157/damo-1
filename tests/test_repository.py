import os
from sealledger.repository import init_db, save_ledger, get_ledger
from sealledger.db import engine


def test_repository_save_and_get(tmp_path, monkeypatch):
    # use sqlite file for a simple integration test
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{db_path}")
    # re-import engine binding
    from importlib import reload
    import sealledger.db as dbmod

    reload(dbmod)
    init_db()
    lid = "001"
    obligations = [{"id": "O1", "type": "test", "owner": "a", "constraint": {}}]
    comp = {"merkle_root": "abc"}
    robust = {"seal_strength": 1.0}
    seals = {"sig": "00"}
    save_ledger(lid, obligations, comp, robust, seals, input_snapshot={"owner": "a"})
    g = get_ledger(lid)
    assert g is not None
