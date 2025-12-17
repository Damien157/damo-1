from sealledger.ledger import InMemoryLedger
from sealledger.models import Obligation, CompositeResult, RobustnessMetrics


def test_ledger_seal_and_get():
    l = InMemoryLedger()
    ob = Obligation(id="o1", type="test", owner="x", constraint={})
    comp = CompositeResult(id="c1", stitched_payload={}, proof={"merkle_root": "abc", "count": 0})
    r = RobustnessMetrics(seal_strength=1.0, gate_efficacy=1.0, composite_robustness=1.0, confidence=1.0)
    entry = l.seal([ob], comp, r, seals={"sig": "00"})
    got = l.get(entry.ledger_id)
    assert got.ledger_id == entry.ledger_id
