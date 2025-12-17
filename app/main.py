from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sealledger.obligations import extract_obligations, verify_premises, bond_obligation
from sealledger.crypto import generate_ed25519_keypair, verify
from sealledger.kms import LocalKMS
from sealledger.gate import Gate
from sealledger.stitcher import Stitcher
from sealledger.robustness import quantify
import os
from sealledger.ledger import ledger
from sealledger import repository

app = FastAPI(title="SealedLedger Prototype")


class IngestRequest(BaseModel):
    data: dict


@app.post("/ingest")
def ingest(req: IngestRequest):
    obs = extract_obligations(req.data)
    return {"job_id": "ingest-1", "obligations": [o.dict() for o in obs]}


@app.post("/bond/{obligation_id}")
def bond(obligation_id: str, payload: IngestRequest):
    obs = extract_obligations(payload.data)
    ob = next((o for o in obs if o.id == obligation_id), None)
    if not ob:
        raise HTTPException(status_code=404, detail="obligation not found")
    premises = verify_premises(ob, payload.data)
    # use configured signer
    signer_type = os.getenv("SIGNER", "local")
    if signer_type == "local":
        kms = LocalKMS()
    else:
        kms = LocalKMS()
    ob2 = bond_obligation(ob, premises, signer=kms)
    return {"obligation": ob2.dict(), "signer": kms.generate_keypair()[1].hex()}


@app.post("/transform")
def transform(req: dict):
    g = Gate()
    obs = extract_obligations(req.get("data", {}))
    cls = g.classify(req.get("transform", {}), obs, req.get("data", {}))
    return {"classification": cls}


@app.post("/stitch")
def stitch(req: dict):
    s = Stitcher()
    signals = [
        # naive wrapping
        type("S", (), {"id": k, "source": v.get("source", "src"), "payload": v.get("payload")})()
        for k, v in req.get("signals", {}).items()
    ]
    # convert to PartialSignal-like objects for prototype
    from sealledger.models import PartialSignal

    ps = [PartialSignal(id=s.id, source=s.source, payload=s.payload) for s in signals]
    comp = s.stitch(ps)
    return {"composite": comp.dict()}


@app.post("/seal-ledger")
def seal_ledger(req: dict):
    obs = [o for o in req.get("obligations", [])]
    from sealledger.models import Obligation as OB, CompositeResult, RobustnessMetrics

    obligations = [OB(**o) if isinstance(o, dict) else o for o in obs]
    composite = CompositeResult(**req.get("composite"))
    robustness = RobustnessMetrics(**req.get("robustness"))
    seals = req.get("seals", {})
    input_snapshot = req.get("input_snapshot")
    # choose persistent or in-memory ledger based on env
    if os.getenv("PERSISTENT_LEDGER", "0") == "1":
        # ensure DB is initialised
        repository.init_db()
        repository.save_ledger(req.get("ledger_id", ""), [o.dict() if hasattr(o, "dict") else o for o in obligations], req.get("composite"), req.get("robustness"), seals, input_snapshot=input_snapshot)
        return {"ledger_id": req.get("ledger_id", "")}
    else:
        entry = ledger.seal(obligations, composite, robustness, seals, input_snapshot=input_snapshot)
        return {"ledger_id": entry.ledger_id}


@app.get("/ledger/{ledger_id}")
def get_ledger(ledger_id: str):
    try:
        e = ledger.get(ledger_id)
        return e.dict()
    except Exception:
        raise HTTPException(status_code=404, detail="ledger not found")


@app.get("/ledger/{ledger_id}/replay")
def replay_ledger(ledger_id: str):
    try:
        e = ledger.get(ledger_id)
        # re-verify obligations using stored input snapshot when available
        from sealledger.obligations import verify_premises

        snapshot = e.input_snapshot or {}
        verifications = {}
        for ob in e.obligations:
            p = verify_premises(ob, snapshot)
            verifications[ob.id] = p
        return {"ledger_id": ledger_id, "verifications": verifications, "input_snapshot": snapshot}
    except Exception:
        raise HTTPException(status_code=404, detail="ledger not found")
